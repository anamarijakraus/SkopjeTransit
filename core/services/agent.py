import json
import re
from datetime import date
from openai import OpenAI, BadRequestError
from django.conf import settings
from . import transit

MODEL = "meta-llama/llama-3.3-70b-instruct"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.OPENROUTER_API_KEY or "not-configured",
)

_KNOWN_TOOLS = {"search_rides", "book_ride", "get_bus_schedule", "answer_faq"}


def _parse_inline_tool_call(content):
    """
    Some models write tool calls as JSON text or Python-style function calls in the
    reply instead of using the tool_calls API field. This detects both patterns and
    returns (tool_name, params) so the agent loop can execute the tool properly.
    """
    if not content:
        return None

    # Pattern 1: JSON object — {"name": "...", "parameters": {...}}
    for m in re.finditer(r'\{', content):
        start = m.start()
        depth = 0
        for i, ch in enumerate(content[start:]):
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    try:
                        obj = json.loads(content[start:start + i + 1])
                    except json.JSONDecodeError:
                        break
                    name = obj.get("name") or obj.get("function")
                    params = obj.get("parameters") or obj.get("arguments") or obj.get("input")
                    if name in _KNOWN_TOOLS and isinstance(params, dict):
                        return name, params
                    break

    # Pattern 2: Python-style call — tool_name(key="value", ...)
    py_match = re.search(r'(\w+)\(([^)]*)\)', content)
    if py_match:
        name = py_match.group(1)
        if name in _KNOWN_TOOLS:
            params = {}
            for kv in re.finditer(r'(\w+)\s*=\s*"((?:[^"\\]|\\.)*)"', py_match.group(2)):
                params[kv.group(1)] = kv.group(2)
            if params:
                return name, params

    return None


TOOLS = [
    {"type": "function", "function": {
        "name": "search_rides",
        "description": (
            "Search for available carpool rides. Pass the stop names exactly as the user said — "
            "the tool will resolve partial names automatically and ask for clarification if needed."
        ),
        "parameters": {"type": "object", "properties": {
            "pickup": {"type": "string", "description": "Pickup stop name (partial OK)"},
            "dropoff": {"type": "string", "description": "Dropoff stop name (partial OK)"},
            "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
            "time": {"type": "string", "description": "Time in HH:MM format"},
        }, "required": ["pickup", "dropoff", "date", "time"]},
    }},
    {"type": "function", "function": {
        "name": "book_ride",
        "description": "Book a carpool ride. Only call after the user has confirmed how many seats they want AND explicitly confirmed the booking.",
        "parameters": {"type": "object", "properties": {
            "ride_id": {"type": "integer"},
            "pickup_stop": {"type": "string", "description": "Exact stop name where passenger boards"},
            "seats": {"type": "integer", "description": "Number of seats to book"},
        }, "required": ["ride_id", "pickup_stop", "seats"]},
    }},
    {"type": "function", "function": {
        "name": "get_bus_schedule",
        "description": (
            "Get bus lines between two stops. Call automatically if no carpool found. "
            "Pass the stop names exactly as the user said — partial names are resolved automatically."
        ),
        "parameters": {"type": "object", "properties": {
            "pickup": {"type": "string", "description": "Pickup stop name (partial OK)"},
            "dropoff": {"type": "string", "description": "Dropoff stop name (partial OK)"},
            "time": {"type": "string", "description": "Optional HH:MM to find buses at or after this time"},
        }, "required": ["pickup", "dropoff"]},
    }},
    {"type": "function", "function": {
        "name": "answer_faq",
        "description": "Answer a FAQ about the SkopjeTransit service.",
        "parameters": {"type": "object", "properties": {
            "question": {"type": "string"},
        }, "required": ["question"]},
    }},
]


def build_system_prompt(stop_names):
    from datetime import timedelta
    today = date.today()
    tomorrow = today + timedelta(days=1)
    day_after = today + timedelta(days=2)
    today_str    = today.strftime("%Y-%m-%d")
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")
    day_after_str = day_after.strftime("%Y-%m-%d")
    today_weekday    = today.strftime("%A")
    tomorrow_weekday = tomorrow.strftime("%A")
    day_after_weekday = day_after.strftime("%A")
    stops_preview = ", ".join(stop_names[:25])
    if len(stop_names) > 25:
        stops_preview += f"... (+{len(stop_names) - 25} more)"
    return f"""LANGUAGE: Respond in English only, always. Never use Macedonian or Cyrillic.

You are the SkopjeTransit Ride Assistant — warm, conversational, and helpful.
You help users: (1) find and book carpool rides, (2) check bus schedules, (3) answer FAQs.

Current date reference (use these EXACT strings when calling tools — never calculate yourself):
  "today"          → {today_str} ({today_weekday})
  "tomorrow"       → {tomorrow_str} ({tomorrow_weekday})
  "day after tomorrow" → {day_after_str} ({day_after_weekday})

When the user says "today", always use {today_str}.
When the user says "tomorrow", always use {tomorrow_str}.
For "next [weekday]", count forward from {today_str} to find the correct YYYY-MM-DD.

Known stop names (tools also accept partial names):
{stops_preview}

════════════════════════════════════════
CRITICAL — TOOL CALLING RULES
════════════════════════════════════════
1. NEVER output tool calls as JSON text. Use the function-calling API only.
   Never say "Here's the function call", never show JSON, never describe what you're about to call.
   When you have all the info, just call the tool silently and present its result.

2. NEVER call a tool until you have ALL required values confirmed in the conversation:
   - search_rides requires: pickup stop, dropoff stop, date, AND departure time.
   - get_bus_schedule requires: pickup stop AND dropoff stop. Do NOT ask the user for a time.
     However, if the user already mentioned a time in their request, pass it as the "time" field.

If the user gives a vague request WITHOUT providing the required values, do NOT call any tool.
This includes messages like:
  "I want to book a carpool ride."
  "Book a ride for me."
  "Show me all available rides."
  "Find a bus."
  "Check the schedule."
Instead, ask ONE friendly question to collect the first missing piece of information.
Continue asking one question at a time until you have everything you need.

Example flow:
  User: "I want to book a carpool ride."
  You:  "Of course! Which stop are you departing from?"
  User: "Aerodrom"
  You:  "Got it — and where are you headed?"
  User: "City Park"
  You:  "What date would you like to travel?"
  User: "Tomorrow"
  You:  "And what time do you want to depart?"
  User: "5pm"
  → Now call search_rides with all four values.

NEVER call search_rides, book_ride, or get_bus_schedule the moment the user says they want
to book or find a ride. You must collect ALL required fields first through conversation.

════════════════════════════════════════
DATE & TIME PARSING
════════════════════════════════════════
Always convert natural language dates and times to YYYY-MM-DD and HH:MM BEFORE calling any tool.
Use the exact date strings from the reference table above — do NOT calculate dates yourself.

  "today"          → {today_str}
  "tomorrow"       → {tomorrow_str}
  "day after tmrw" → {day_after_str}
  "tonight"        → {today_str}
  "5pm" / "17:00"  → 17:00
  "6pm" / "18:00"  → 18:00
  "half past 3"    → 15:30
  "noon"           → 12:00
  "midnight"       → 00:00

For "next [weekday]" count forward from {today_str}.
If the user gives all four values (pickup, dropoff, date, time) in one message, call the tool immediately.

════════════════════════════════════════
STOP DISAMBIGUATION
════════════════════════════════════════
- Tools accept partial names and resolve them automatically.
- If a tool returns "disambiguation_needed": show the options as a numbered list and ask which one.
  When the user replies (by number OR by name OR "the first one" etc.), map their answer to the
  EXACT stop name from the list and call the tool again using that exact string — never the user's
  raw words. For example, if options are ["Vlae", "Vlae Porta"] and the user says "the first one",
  call the tool with pickup="Vlae".
- If a tool returns "stop_not_found": tell the user politely and ask them to rephrase or try a
  nearby landmark name.

════════════════════════════════════════
RIDE BOOKING FLOW
════════════════════════════════════════
1. Collect pickup, dropoff, date, time — one question at a time if needed.
2. Call search_rides once you have all four.
   IMPORTANT — before calling search_rides, verify the requested date is today or in the future.
   If the user gives a past calendar date (a date before today, {today_str}):
     Respond with: "That date has already passed — please choose a future date."
     Do NOT call search_rides. Do NOT suggest buses or anything else. Just ask for a valid date.
   If search_rides returns {{"error": "past_date"}}, do exactly the same.
   Note: if today's date is given but the time has already passed, still call search_rides — the app handles that gracefully.
3. If carpool_found=true: output EXACTLY the following line and nothing else — no greeting,
   no numbered list, no explanation, no follow-up sentence:
   RIDE_OPTIONS:<paste the exact value of the "rides" key from the tool result as compact JSON>
   Example: RIDE_OPTIONS:[{{"id":5,"driver_name":"Ana","departure_time":"2026-06-07T22:00:00","seat_price":"200","available_seats":3,"start_location":"Vlae","end_location":"Centar"}}]
   The app will render interactive ride cards for the user to click and select.
   After the user selects a ride they will send a message containing "ride ID: X".
   When you see that, extract the ride_id, then ask: "How many seats would you like to book?"
   Wait for their seat count, then show a confirmation summary BEFORE calling book_ride:
     "Just to confirm — [N] seat(s) with [driver], departing at [HH:MM], total [N × price] MKD. Shall I book this?"
   Only call book_ride after the user explicitly says yes / confirm / go ahead / book it.
   Never call book_ride without this explicit confirmation.
4. If carpool_found=false and buses_found=true and direct=true: FIRST say in one sentence
   that no carpool rides are available for that route and time, THEN show direct buses as
   a fallback using the BUS FORMAT below.
5. If carpool_found=false and buses_found=true and direct=false: FIRST say in one sentence
   that no carpool rides are available, THEN tell the user there's no direct bus but list
   buses departing from their stop using BUS FORMAT.
6. If carpool_found=false and buses_found=false: apologise and say nothing was found.
7. Never assume 1 seat — always ask first.
8. The bus fallback already filters by the passenger's requested time — buses shown will
   depart at or after that time, so do not re-filter or explain the times.

════════════════════════════════════════
BUS FORMAT — MANDATORY
════════════════════════════════════════
List every bus result as a bullet using EXACTLY this pattern (24-hour HH:MM, → arrow):
- Bus {{name}}: {{pickup_stop}} {{HH:MM}} → {{dropoff_stop}} {{HH:MM}}
Example:
- Bus 22: Vlae Porta 17:42 → Centar Record 18:42
- Bus 4: Vlae 17:48 → Centar Record 18:42
Rules:
- ALWAYS use this exact format for every bus, including departure-only results.
- For departure-only buses (direct=false), the tool result includes "end_stop" and "end_time" —
  use those as the dropoff_stop and dropoff time in the format above.
- 24-hour time only. Use the → character (not -> or other arrows). Nothing else on the same bullet line.
- No bold, no extra punctuation, no notes on the same line.
One short intro sentence before the list. One short follow-up sentence after.

════════════════════════════════════════
FAQ BEHAVIOUR
════════════════════════════════════════
There are two distinct FAQ situations — handle them differently:

1. User wants to BROWSE / SEE the FAQ list (e.g. "show me your questions", "what can I ask",
   "I want to see your FAQ", "do you have an FAQ", "I'd like to ask a question",
   "what questions do you have", "no I want to see your FAQ"):
   → Respond with ONLY the single word: FAQ_LIST
     Nothing before it, nothing after it. Do not call answer_faq.

2. User asks a SPECIFIC question (e.g. "How do I cancel a ride?", "Can I pay with cash?"):
   → Call answer_faq with that question.
   → When answer_faq returns {{"answer": "..."}},  present that answer text EXACTLY as your reply.
     Do NOT paraphrase it. Do NOT add suggestions to "check the FAQ" or "visit the website".
     Just state the answer, then offer to help with anything else in one short sentence.

════════════════════════════════════════
BOOKING CONFIRMATION FORMAT
════════════════════════════════════════
When book_ride returns a result with "success": true, your ENTIRE reply must be ONLY this line:
BOOKING_CONFIRMED:{{"booking_id":<id>,"from":"<from>","to":"<to>","departure":"<departure>","driver":"<driver>","price":"<price>","seats_booked":<seats_booked>,"seats_left":<seats_left>}}

Note: the booking is created as PENDING — the driver must confirm it before it is active.
The card shown to the user already communicates this, so do not add any extra message.

Replace each placeholder with the exact value from the tool result.
Do NOT add any other words, sentences, or punctuation — just that one line.
The departure value comes from the tool result as-is (e.g. "2026-05-13T18:47").

════════════════════════════════════════
TONE
════════════════════════════════════════
- Be encouraging and natural. Use short sentences. Never sound robotic.
- When asking follow-up questions, keep them light: "Got it! Where are you headed?"
- After completing a task, offer to help with something else in one sentence."""


def _resolve_stop(name: str):
    """
    Returns (resolved_name, status) where status is:
      'ok'               – exactly one match, resolved_name is the DB name
      'disambiguation'   – multiple matches, resolved_name is a list of options
      'not_found'        – no matches
    """
    matches = transit.find_matching_stops(name)
    if len(matches) == 1:
        return matches[0], "ok"
    if len(matches) > 1:
        return matches, "disambiguation"
    return [], "not_found"


def dispatch_tool(tool_name, tool_input, user=None):
    if tool_name == "search_rides":
        pickup_raw = tool_input["pickup"].strip()
        dropoff_raw = tool_input["dropoff"].strip()

        if not pickup_raw or not dropoff_raw:
            return json.dumps({"error": "Missing stop names. Ask the user for pickup and dropoff stops before calling this tool."})

        if not tool_input.get("date"):
            return json.dumps({"error": "Missing date. Ask the user what date they want to travel before calling this tool."})

        if not tool_input.get("time"):
            return json.dumps({"error": "Missing departure time. Ask the user what time they want to depart before calling this tool."})

        # Reject if the requested calendar date is strictly before today
        try:
            from datetime import date as _date
            req_date = _date.fromisoformat(tool_input['date'])
            if req_date < _date.today():
                return json.dumps({"error": "past_date", "message": "That date has already passed."})
        except (ValueError, KeyError):
            pass

        # Resolve stops for bus fallback; carpool search uses raw names (fuzzy/case-insensitive)
        pickup, pickup_status = _resolve_stop(pickup_raw)
        if pickup_status == "disambiguation":
            return json.dumps({"disambiguation_needed": True, "field": "pickup", "options": pickup})

        dropoff, dropoff_status = _resolve_stop(dropoff_raw)
        if dropoff_status == "disambiguation":
            return json.dumps({"disambiguation_needed": True, "field": "dropoff", "options": dropoff})

        # Always try carpool first using raw names — ride start/end locations are free text
        # Ride start/end locations are free-text entered by drivers — always match
        # against the raw user input, not the resolved bus Stop name.
        try:
            rides = transit.find_carpools(pickup_raw, dropoff_raw, tool_input["date"], tool_input["time"])
        except (ValueError, TypeError):
            rides = []
        if rides:
            return json.dumps({"carpool_found": True, "rides": rides})

        # Bus fallback requires stops to exist in the Stop table
        if pickup_status == "not_found":
            return json.dumps({
                "carpool_found": False,
                "buses_found": False,
                "message": f"No carpool found and '{pickup_raw}' is not served by any bus line.",
            })
        if dropoff_status == "not_found":
            return json.dumps({
                "carpool_found": False,
                "buses_found": False,
                "message": f"No carpool found and '{dropoff_raw}' is not served by any bus line.",
            })

        # Fallback 1: direct buses between the two stops
        buses = transit.find_buses(pickup, dropoff, tool_input.get("time"))
        if buses:
            return json.dumps({
                "carpool_found": False,
                "buses_found": True,
                "direct": True,
                "buses": [
                    {
                        "bus_name": b["bus_name"],
                        "pickup_stop": b["pickup_stop"],
                        "dropoff_stop": b["dropoff_stop"],
                        "pickup_time": b["pickup_time"],
                        "dropoff_time": b["dropoff_time"],
                    }
                    for b in buses
                ],
            })

        # Fallback 2: all departures from the pickup stop
        departures = transit.find_departures_at_stop(pickup, tool_input.get("time"))
        if departures:
            return json.dumps({
                "carpool_found": False,
                "buses_found": True,
                "direct": False,
                "pickup_stop": pickup,
                "note": "No direct bus to the destination, but these buses depart from your pickup stop.",
                "buses": departures,
            })

        return json.dumps({
            "carpool_found": False,
            "buses_found": False,
            "message": "No carpool rides or buses found at this stop and time.",
        })

    elif tool_name == "book_ride":
        if not user or not user.is_authenticated:
            return json.dumps({"success": False, "error": "Not authenticated."})
        seats = max(1, int(tool_input.get("seats", 1)))
        return json.dumps(transit.create_booking(user, tool_input["ride_id"], tool_input["pickup_stop"], seats=seats))

    elif tool_name == "get_bus_schedule":
        pickup_raw = tool_input["pickup"].strip()
        dropoff_raw = tool_input["dropoff"].strip()

        pickup, pickup_status = _resolve_stop(pickup_raw)
        if pickup_status == "disambiguation":
            return json.dumps({"disambiguation_needed": True, "field": "pickup", "options": pickup})
        if pickup_status == "not_found":
            return json.dumps({"stop_not_found": True, "field": "pickup", "query": pickup_raw})

        dropoff, dropoff_status = _resolve_stop(dropoff_raw)
        if dropoff_status == "disambiguation":
            return json.dumps({"disambiguation_needed": True, "field": "dropoff", "options": dropoff})
        if dropoff_status == "not_found":
            return json.dumps({"stop_not_found": True, "field": "dropoff", "query": dropoff_raw})

        from datetime import datetime as _dt
        bus_time = tool_input.get("time") or _dt.now().strftime("%H:%M")
        buses = transit.find_buses(pickup, dropoff, bus_time)
        if buses:
            return json.dumps({"found": True, "buses": [
                {
                    "bus_name": b["bus_name"],
                    "pickup_stop": b["pickup_stop"],
                    "dropoff_stop": b["dropoff_stop"],
                    "pickup_time": b["pickup_time"],
                    "dropoff_time": b["dropoff_time"],
                }
                for b in buses
            ]})
        return json.dumps({"found": False, "message": "No direct bus found between these stops."})

    elif tool_name == "answer_faq":
        import os
        from difflib import get_close_matches
        faq_path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/faq.json"))
        with open(faq_path) as f:
            faqs = json.load(f)
        questions = [item["q"].lower() for item in faqs]
        matches = get_close_matches(tool_input["question"].lower(), questions, n=1, cutoff=0.35)
        if matches:
            answer = next(item["a"] for item in faqs if item["q"].lower() == matches[0])
            return json.dumps({"answer": answer})
        return json.dumps({"answer": "I don't have a specific answer. Contact us at skopje@transit.mk or +389 75 180 423."})

    return json.dumps({"error": f"Unknown tool: {tool_name}"})


def _booking_confirmation(tool_name: str, result_json: str):
    """Return a BOOKING_CONFIRMED: signal string if book_ride succeeded, else None."""
    if tool_name != "book_ride":
        return None
    try:
        data = json.loads(result_json)
    except (json.JSONDecodeError, TypeError):
        return None
    if not data.get("success"):
        return None
    return "BOOKING_CONFIRMED:" + json.dumps({
        "booking_id":   data["booking_id"],
        "from":         data["from"],
        "to":           data["to"],
        "departure":    data["departure"],
        "driver":       data["driver"],
        "price":        data["price"],
        "seats_booked": data.get("seats_booked", 1),
        "seats_left":   data["seats_left"],
    })


_FALLBACK_MSG = "I'm having trouble connecting right now — please try again in a moment."


def run_agent(user_message, history, user=None):
    from openai import APITimeoutError, APIConnectionError, APIStatusError
    stop_names = transit.get_all_stop_names()
    system_prompt = build_system_prompt(stop_names)
    messages = history + [{"role": "user", "content": user_message}]
    inline_call_attempts = 0

    while True:
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "system", "content": system_prompt}] + messages,
                tools=TOOLS,
                tool_choice="auto",
                max_tokens=1024,
                timeout=30,
            )
        except APITimeoutError:
            return _FALLBACK_MSG, messages
        except APIConnectionError:
            return _FALLBACK_MSG, messages
        except APIStatusError as exc:
            if exc.status_code >= 500:
                return _FALLBACK_MSG, messages
            raise
        except BadRequestError as exc:
            if "tool_use_failed" in str(exc) and messages[-1].get("role") != "user":
                raise
            if "tool_use_failed" in str(exc):
                messages.append({
                    "role": "user",
                    "content": "(Please call the tool using the standard function-calling interface.)",
                })
                continue
            raise

        msg = response.choices[0].message
        assistant_msg = {"role": "assistant", "content": msg.content or ""}
        if msg.tool_calls:
            assistant_msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in msg.tool_calls
            ]
        messages.append(assistant_msg)

        if not msg.tool_calls:
            # Fallback: model wrote the tool call as JSON text instead of using the API
            inline = _parse_inline_tool_call(msg.content or "")
            if inline and inline_call_attempts < 2:
                inline_call_attempts += 1
                tool_name, tool_input = inline
                fake_id = f"inline_{inline_call_attempts}"
                # Rewrite last assistant message so history is clean for the next turn
                messages[-1] = {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [{
                        "id": fake_id,
                        "type": "function",
                        "function": {"name": tool_name, "arguments": json.dumps(tool_input)},
                    }],
                }
                result = dispatch_tool(tool_name, tool_input, user=user)
                messages.append({"role": "tool", "tool_call_id": fake_id, "content": result})
                confirmation = _booking_confirmation(tool_name, result)
                if confirmation:
                    messages.append({"role": "assistant", "content": confirmation})
                    return confirmation, messages
                continue

            return msg.content, messages

        for tc in msg.tool_calls:
            tool_input = json.loads(tc.function.arguments)
            result = dispatch_tool(tc.function.name, tool_input, user=user)
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
            confirmation = _booking_confirmation(tc.function.name, result)
            if confirmation:
                messages.append({"role": "assistant", "content": confirmation})
                return confirmation, messages

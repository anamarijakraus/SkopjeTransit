import json
import os
import random
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from core.services.agent import run_agent

_FAQ_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'faq.json')

SESSION_RAW       = 'assistant_raw_history'
SESSION_VIS       = 'assistant_history'
SESSION_LAST_GRT  = 'assistant_last_greeting'
SESSION_LAST_BYE  = 'assistant_last_goodbye'

# ── Initial page greetings (shown on fresh load) ──────────────────────────────
_PAGE_GREETINGS = [
    "Hey there! I'm your SkopjeTransit assistant. Need a carpool, want to check bus times, or just have a question? I'm here — what can I help you with?",
    "Hi! Welcome to SkopjeTransit. I can find you a carpool ride, look up bus schedules, or answer anything about the service. Where would you like to start?",
    "Hello! Ready to help you get around Skopje. Whether it's a carpool, a bus, or a quick question — just ask. What do you need today?",
    "Good to see you! I'm the SkopjeTransit assistant. Tell me where you're going and I'll help you get there. What's on your mind?",
    "Hey! Looking for a ride or checking the bus? I've got you covered. What would you like to do?",
    "Hi there! I'm here to make your journey around Skopje a little easier. Carpools, buses, FAQs — ask away. What can I help you with?",
    "Welcome! I'm your SkopjeTransit AI assistant. Let me know what you're looking for — a carpool, a bus schedule, or anything else transit-related.",
]

# ── In-chat greeting replies ──────────────────────────────────────────────────
_CHAT_GREETINGS = [
    "Hey! Where are you headed today?",
    "Hi there! Need a ride or have a question?",
    "Hello! I'm here to help with routes, carpools, or anything transit.",
    "Hey, good to see you! What can I help you with?",
    "Hi! Planning a trip around Skopje?",
]

# ── Goodbye replies ───────────────────────────────────────────────────────────
_GOODBYES = [
    "Safe travels! Come back anytime.",
    "Have a great ride! 👋",
    "Bye! Hope I made your commute easier.",
    "Take care! I'm here whenever you need directions or a carpool.",
    "See you next trip!",
]

# ── Detection keyword sets ────────────────────────────────────────────────────
_GREETING_WORDS = {'hi', 'hello', 'hey', 'sup', 'yo', 'greetings', 'howdy'}
_GREETING_PHRASES = ['good morning', 'good afternoon', 'good evening']

_GOODBYE_WORDS = {'bye', 'goodbye', 'cya', 'later', 'farewell'}
_GOODBYE_PHRASES = ['see you', 'see ya', 'thanks bye', 'thank you bye', 'take care', 'good night']

# Words that indicate a transit question is embedded in the message
_TRANSIT_WORDS = {
    'bus', 'carpool', 'ride', 'route', 'schedule', 'stop', 'fare', 'book',
    'booking', 'cancel', 'pay', 'ticket', 'driver', 'passenger', 'depart',
    'arrive', 'from', 'to', 'when', 'where', 'how', 'price', 'cost',
    'available', 'seats', 'next', 'trip', 'goes', 'get', 'find', 'show',
    'vlae', 'karposh', 'centar', 'aerodrom', 'chair', 'bunjakovec',
}


def _has_greeting(lower: str) -> bool:
    words = set(lower.split())
    return bool(words & _GREETING_WORDS) or any(p in lower for p in _GREETING_PHRASES)


def _has_goodbye(lower: str) -> bool:
    words = set(lower.split())
    return bool(words & _GOODBYE_WORDS) or any(p in lower for p in _GOODBYE_PHRASES)


def _has_transit(lower: str) -> bool:
    words = set(lower.split())
    return bool(words & _TRANSIT_WORDS)


def _pick(responses: list, session_key: str, session) -> str:
    """Pick a random response, avoiding the last one used."""
    last = session.get(session_key)
    choices = [r for r in responses if r != last] or responses
    chosen = random.choice(choices)
    session[session_key] = chosen
    session.modified = True
    return chosen


def _shortcircuit_reply(message: str, session) -> str | None:
    """
    Return a canned reply if the message is a pure greeting or goodbye.
    Returns None if the message should be forwarded to the LLM agent.
    """
    lower = message.lower().strip()
    is_greeting = _has_greeting(lower)
    is_goodbye  = _has_goodbye(lower)
    has_transit = _has_transit(lower)

    # Combined greeting + real question → let agent handle it
    if has_transit:
        return None

    if is_goodbye:
        return _pick(_GOODBYES, SESSION_LAST_BYE, session)

    if is_greeting:
        return _pick(_CHAT_GREETINGS, SESSION_LAST_GRT, session)

    return None


def get_visible(raw_history):
    """Extract only user/assistant text turns for display."""
    visible = []
    for msg in raw_history:
        if msg.get('role') == 'user' and not msg.get('content', '').startswith('__'):
            visible.append({'role': 'user', 'content': msg['content']})
        elif msg.get('role') == 'assistant' and msg.get('content'):
            visible.append({'role': 'assistant', 'content': msg['content']})
    return visible


def _save_reply(request, user_message, reply, raw_history):
    """Persist a reply (canned or LLM) to the session."""
    updated = raw_history + [
        {'role': 'user',      'content': user_message},
        {'role': 'assistant', 'content': reply},
    ]
    request.session[SESSION_RAW] = updated[-30:]
    request.session[SESSION_VIS] = get_visible(updated[-30:])
    request.session.modified = True


@login_required
def assistant_view(request):
    raw_history = request.session.get(SESSION_RAW, [])

    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()
        if not user_message:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Empty message'}, status=400)
            return redirect('core:assistant')

        # Try canned greeting/goodbye first (no LLM call needed)
        canned = _shortcircuit_reply(user_message, request.session)
        if canned:
            _save_reply(request, user_message, canned, raw_history)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'reply': canned})
            return redirect('core:assistant')

        # Forward to LLM agent
        try:
            reply, updated_raw = run_agent(user_message, raw_history, user=request.user)
        except Exception as exc:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': str(exc)}, status=500)
            return redirect('core:assistant')

        request.session[SESSION_RAW] = updated_raw[-30:]
        request.session[SESSION_VIS] = get_visible(updated_raw[-30:])
        request.session.modified = True

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'reply': reply})
        return redirect('core:assistant')

    # GET: always start a fresh conversation
    request.session.pop(SESSION_RAW, None)
    request.session.pop(SESSION_VIS, None)
    greeting_reply = random.choice(_PAGE_GREETINGS)
    request.session[SESSION_RAW] = []
    request.session[SESSION_VIS] = [{'role': 'assistant', 'content': greeting_reply}]
    request.session.modified = True

    from core.views import BUS_STOPS, STOP_COORDINATES  # local import avoids circular dep

    with open(_FAQ_PATH) as f:
        faqs = json.load(f)

    return render(request, 'core/assistant.html', {
        'messages': request.session.get(SESSION_VIS, []),
        'faqs_json': json.dumps(faqs),
        'initial_panel': 'greeting',
        'bus_stops_json': json.dumps(BUS_STOPS),
        'stop_coordinates_json': json.dumps(STOP_COORDINATES),
    })


@login_required
@require_POST
def clear_chat_view(request):
    request.session.pop(SESSION_RAW, None)
    request.session.pop(SESSION_VIS, None)
    request.session.modified = True
    return redirect('core:assistant')

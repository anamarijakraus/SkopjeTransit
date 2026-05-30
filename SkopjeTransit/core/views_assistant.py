import json
import os
import random
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from core.services.agent import run_agent

_FAQ_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'faq.json')

SESSION_RAW = 'assistant_raw_history'
SESSION_VIS = 'assistant_history'

_GREETINGS = [
    "Hey there! I'm your SkopjeTransit assistant. Need a carpool, want to check bus times, or just have a question? I'm here — what can I help you with?",
    "Hi! Welcome to SkopjeTransit. I can find you a carpool ride, look up bus schedules, or answer anything about the service. Where would you like to start?",
    "Hello! Ready to help you get around Skopje. Whether it's a carpool, a bus, or a quick question — just ask. What do you need today?",
    "Good to see you! I'm the SkopjeTransit assistant. Tell me where you're going and I'll help you get there. What's on your mind?",
    "Hey! Looking for a ride or checking the bus? I've got you covered. What would you like to do?",
    "Hi there! I'm here to make your journey around Skopje a little easier. Carpools, buses, FAQs — ask away. What can I help you with?",
    "Welcome! I'm your SkopjeTransit AI assistant. Let me know what you're looking for — a carpool, a bus schedule, or anything else transit-related.",
]


def get_visible(raw_history):
    """Extract only user/assistant text turns for display."""
    visible = []
    for msg in raw_history:
        if msg.get('role') == 'user' and not msg.get('content', '').startswith('__'):
            visible.append({'role': 'user', 'content': msg['content']})
        elif msg.get('role') == 'assistant' and msg.get('content'):
            visible.append({'role': 'assistant', 'content': msg['content']})
    return visible


@login_required
def assistant_view(request):
    raw_history = request.session.get(SESSION_RAW, [])

    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()
        if not user_message:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Empty message'}, status=400)
            return redirect('core:assistant')

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
    greeting_reply = random.choice(_GREETINGS)
    request.session[SESSION_RAW] = []  # greeting is display-only, not sent to the API
    request.session[SESSION_VIS] = [{'role': 'assistant', 'content': greeting_reply}]
    request.session.modified = True

    visible_messages = request.session.get(SESSION_VIS, [])

    with open(_FAQ_PATH) as f:
        faqs = json.load(f)

    initial_panel = 'greeting'

    return render(request, 'core/assistant.html', {
        'messages': visible_messages,
        'faqs_json': json.dumps(faqs),
        'initial_panel': initial_panel,
    })


@login_required
@require_POST
def clear_chat_view(request):
    request.session.pop(SESSION_RAW, None)
    request.session.pop(SESSION_VIS, None)
    request.session.modified = True
    return redirect('core:assistant')

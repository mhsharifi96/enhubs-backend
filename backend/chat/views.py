from django.conf import settings
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from openai import OpenAI
from .models import ConversationLog
from lessons.models import AudioHistory

# ✅ initialize OpenAI client with base_url and api_key
client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL,  # 👈 customizable
)


class StartConversationAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        if  ConversationLog.objects.filter(user=user).count()> 10:
            return Response({"error": "You have reached the maximum number of 10 active conversations."},
                             status=status.HTTP_429_TOO_MANY_REQUESTS)

        recent_audio = AudioHistory.objects.filter(user=user).order_by('-updated_at').first()
        if not recent_audio:
            return Response({"reply": "please first listen the audio ...", "conversation_id": ""}, status=status.HTTP_200_OK)
        
        audio_title = recent_audio.audio.title if recent_audio else "General topic"
        audio_transcript = recent_audio.audio.raw_transcript if recent_audio else ""

        prompt = f"""
        You are a friendly English tutor.
        The user recently listened to an audio titled: {audio_title}.
        Transcript: {audio_transcript[:800]}...

        Start a short conversation to help the user practice speaking naturally.
        Ask the first question.

        Instructions for the conversation:
        1. First, **check the user's response** and if it contains grammatical mistakes but is meaningful, **correct it**.
        2. Then, **continue the conversation naturally**.
        3. Use **Markdown formatting** and make **important words and phrases bold**.
        """

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful English tutor who helps users improve speaking."},
                {"role": "user", "content": prompt},
            ]
        )

        text = completion.choices[0].message.content

        # create new conversation log
        log = ConversationLog.objects.create(
            user=user,
            history=[
                {"role": "system", "content": "You are a helpful English tutor who helps users improve speaking."},
                {"role": "user", "content": prompt},
                {"role": "system", "content": "You are a helpful English tutor."},
                {"role": "assistant", "content": text},
            ]
        )

        return Response({"reply": text, "conversation_id": log.id}, status=status.HTTP_200_OK)


class ContinueConversationAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        conversation_id = request.data.get("conversation_id")
        user_message = request.data.get("message")

        if not conversation_id or not user_message:
            return Response({"error": "conversation_id and message are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            log = ConversationLog.objects.get(id=conversation_id, user=user)
        except ConversationLog.DoesNotExist:
            return Response({"error": "Conversation not found."}, status=status.HTTP_404_NOT_FOUND)

        # add user message
        history = log.history
        if len(history)>20:
            return Response({"error": "Conversation too long."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        history.append({"role": "user", "content": user_message})

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=history
        )

        reply = completion.choices[0].message.content

        # append assistant reply
        history.append({"role": "assistant", "content": reply})
        log.history = history
        log.save(update_fields=["history", "updated_at"])

        return Response({"reply": reply, "conversation_id":conversation_id}, status=status.HTTP_200_OK)

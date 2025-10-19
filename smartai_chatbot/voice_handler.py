"""
Voice Handler - Convert speech to text and text to speech
"""

import frappe
import logging
import base64
import io
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class SpeechToTextProcessor:
    """Convert audio to text"""
    
    @staticmethod
    def process_wav(audio_data: str, language: str = "en-US") -> Dict:
        """Process WAV audio and convert to text"""
        try:
            import speech_recognition as sr
            from pydub import AudioSegment
            
            # Decode base64
            audio_bytes = base64.b64decode(audio_data)
            
            # Convert audio
            audio = AudioSegment.from_wav(io.BytesIO(audio_bytes))
            
            # Save temporary file
            temp_path = "/tmp/temp_audio.wav"
            audio.export(temp_path, format="wav")
            
            # Recognize speech
            recognizer = sr.Recognizer()
            with sr.AudioFile(temp_path) as source:
                audio = recognizer.record(source)
            
            try:
                text = recognizer.recognize_google(audio, language=language)
                return {
                    "success": True,
                    "text": text,
                    "language": language,
                    "confidence": 0.9
                }
            except sr.UnknownValueError:
                return {"success": False, "error": "Could not understand audio"}
            except sr.RequestError as e:
                return {"success": False, "error": f"Speech recognition service error: {str(e)}"}
        
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def process_mp3(audio_data: str, language: str = "en-US") -> Dict:
        """Process MP3 audio and convert to text"""
        try:
            import speech_recognition as sr
            from pydub import AudioSegment
            
            # Decode base64
            audio_bytes = base64.b64decode(audio_data)
            
            # Convert MP3 to WAV
            audio = AudioSegment.from_mp3(io.BytesIO(audio_bytes))
            
            # Save temporary file
            temp_path = "/tmp/temp_audio.wav"
            audio.export(temp_path, format="wav")
            
            # Recognize speech
            recognizer = sr.Recognizer()
            with sr.AudioFile(temp_path) as source:
                audio = recognizer.record(source)
            
            try:
                text = recognizer.recognize_google(audio, language=language)
                return {
                    "success": True,
                    "text": text,
                    "language": language,
                }
            except sr.UnknownValueError:
                return {"success": False, "error": "Could not understand audio"}
        
        except Exception as e:
            logger.error(f"Error processing MP3: {str(e)}")
            return {"success": False, "error": str(e)}


class TextToSpeechProcessor:
    """Convert text to audio"""
    
    @staticmethod
    def synthesize(text: str, language: str = "en", voice: str = "male") -> Dict:
        """Synthesize text to speech"""
        try:
            from google.cloud import texttospeech
            import json
            
            # Initialize client
            client = texttospeech.TextToSpeechClient()
            
            # Map language codes
            language_code_map = {
                "en": "en-US",
                "ur": "ur-PK",
                "ar": "ar-SA",
            }
            
            language_code = language_code_map.get(language, "en-US")
            
            # Prepare request
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            voice_config = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                ssml_gender=texttospeech.SsmlVoiceGender.MALE if voice == "male" else texttospeech.SsmlVoiceGender.FEMALE,
            )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.0,
            )
            
            # Synthesize
            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice_config,
                audio_config=audio_config
            )
            
            # Encode to base64
            audio_base64 = base64.b64encode(response.audio_content).decode()
            
            return {
                "success": True,
                "audio": audio_base64,
                "format": "mp3",
                "language": language,
            }
        
        except Exception as e:
            logger.error(f"Error synthesizing speech: {str(e)}")
            return {"success": False, "error": str(e)}


class VoiceHandler:
    """Main voice handler orchestrator"""
    
    def __init__(self):
        self.stt = SpeechToTextProcessor()
        self.tts = TextToSpeechProcessor()
    
    @frappe.whitelist()
    def process_audio_input(self, audio_data: str, format: str = "wav",
                           language: str = "en-US") -> Dict:
        """Process audio input and return text"""
        
        try:
            if format == "wav":
                return self.stt.process_wav(audio_data, language)
            elif format == "mp3":
                return self.stt.process_mp3(audio_data, language)
            else:
                return {"success": False, "error": "Unsupported audio format"}
        
        except Exception as e:
            logger.error(f"Error processing audio input: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @frappe.whitelist()
    def synthesize_response(self, text: str, language: str = "en",
                           voice: str = "male") -> Dict:
        """Synthesize text response to audio"""
        
        try:
            return self.tts.synthesize(text, language, voice)
        
        except Exception as e:
            logger.error(f"Error synthesizing response: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @frappe.whitelist()
    def full_voice_interaction(self, audio_input: str, audio_format: str = "wav",
                              language: str = "en-US", session_id: str = None) -> Dict:
        """Complete voice interaction: audio -> text -> AI response -> audio"""
        
        try:
            # Step 1: Convert audio to text
            text_result = self.process_audio_input(audio_input, audio_format, language)
            if not text_result.get("success"):
                return text_result
            
            user_message = text_result.get("text")
            
            # Step 2: Get AI response (using main chat API)
            from smartai_chatbot.ai_gateway import AIGateway
            
            gateway = AIGateway()
            ai_result = gateway.chat(
                message=user_message,
                session_id=session_id or "voice_session",
                language=language
            )
            
            if not ai_result.get("success"):
                return ai_result
            
            ai_response = ai_result.get("response", "I couldn't generate a response")
            
            # Step 3: Convert response to audio
            lang_code = "en" if language.startswith("en") else ("ur" if language.startswith("ur") else "ar")
            audio_result = self.synthesize_response(ai_response, lang_code)
            
            if not audio_result.get("success"):
                # Return just text if audio synthesis fails
                return {
                    "success": True,
                    "user_input": user_message,
                    "ai_response": ai_response,
                    "audio": None,
                    "audio_error": "Could not synthesize audio"
                }
            
            return {
                "success": True,
                "user_input": user_message,
                "ai_response": ai_response,
                "audio": audio_result.get("audio"),
                "provider": ai_result.get("provider"),
            }
        
        except Exception as e:
            logger.error(f"Error in voice interaction: {str(e)}")
            return {"success": False, "error": str(e)}


# Public API endpoints
@frappe.whitelist()
def process_audio_input(audio_data, format="wav", language="en-US"):
    handler = VoiceHandler()
    return handler.process_audio_input(audio_data, format, language)


@frappe.whitelist()
def synthesize_response(text, language="en", voice="male"):
    handler = VoiceHandler()
    return handler.synthesize_response(text, language, voice)


@frappe.whitelist()
def full_voice_interaction(audio_input, audio_format="wav", language="en-US", session_id=None):
    handler = VoiceHandler()
    return handler.full_voice_interaction(audio_input, audio_format, language, session_id)

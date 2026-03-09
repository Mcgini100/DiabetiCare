"""
DiabetiCare AI Service — Powered by Google Gemini
Provides food image analysis and glucometer OCR.
"""
import os
import json
import re
import base64

# Lazy-load Gemini SDK
_model = None


def _get_model():
    """Initialize Gemini model lazily."""
    global _model
    if _model is not None:
        return _model

    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return None

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        _model = genai.GenerativeModel('gemini-2.0-flash')
        return _model
    except Exception as e:
        print(f'[AI] Gemini init error: {e}')
        return None


def _parse_json_response(text):
    """Extract JSON from Gemini response (handles markdown code blocks)."""
    # Try to extract JSON from markdown code block
    match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if match:
        text = match.group(1)
    # Try parsing directly
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        return None


def analyze_food_image(image_bytes, mime_type='image/jpeg'):
    """
    Analyze a food image and return nutritional breakdown.

    Returns dict with:
        food_items: str - description of foods detected
        meal_type: str - suggested meal type (breakfast, lunch, dinner, snack)
        calories: int - estimated total calories
        carbs_grams: float - estimated carbohydrates in grams
        protein_grams: float - estimated protein in grams
        fat_grams: float - estimated fat in grams
        fiber_grams: float - estimated fiber in grams
        portion_size: str - estimated portion size (small, medium, large)
        health_notes: str - diabetes-specific dietary advice
        confidence: str - confidence level (low, medium, high)
    """
    model = _get_model()
    if model is None:
        return {'error': 'AI service not configured. Please set GEMINI_API_KEY.'}

    prompt = """You are a nutrition expert AI for a diabetes management app.
Analyze this food image and provide a detailed nutritional breakdown.

Return ONLY valid JSON (no markdown, no explanation) with this exact structure:
{
    "food_items": "comma-separated list of all food items you can identify",
    "meal_type": "breakfast|lunch|dinner|snack",
    "calories": estimated total calories as integer,
    "carbs_grams": estimated carbohydrates in grams as float,
    "protein_grams": estimated protein in grams as float,
    "fat_grams": estimated fat in grams as float,
    "fiber_grams": estimated fiber in grams as float,
    "portion_size": "small|medium|large",
    "health_notes": "brief diabetes-specific advice about this meal (e.g. glycemic impact, suggestions)",
    "confidence": "low|medium|high"
}

Be as accurate as possible with calorie and nutrient estimates based on typical serving sizes visible in the image.
If you cannot identify food in the image, set confidence to "low" and estimate conservatively.
Consider common African/Zimbabwean foods if they appear (sadza, kapenta, muriwo, etc.)."""

    try:
        response = model.generate_content([
            prompt,
            {'mime_type': mime_type, 'data': image_bytes}
        ])
        result = _parse_json_response(response.text)
        if result is None:
            return {'error': 'Could not parse AI response. Please try again.'}
        return result
    except Exception as e:
        return {'error': f'AI analysis failed: {str(e)}'}


def read_glucometer_image(image_bytes, mime_type='image/jpeg'):
    """
    Read a glucose value from a glucometer display image.

    Returns dict with:
        value: float - the glucose reading in mmol/L
        unit: str - the unit detected (mmol/L or mg/dL)
        value_mmol: float - value converted to mmol/L
        device_info: str - any device/brand info detected
        confidence: str - confidence level (low, medium, high)
    """
    model = _get_model()
    if model is None:
        return {'error': 'AI service not configured. Please set GEMINI_API_KEY.'}

    prompt = """You are a medical device OCR expert for a diabetes management app.
Look at this image of a glucometer (blood glucose meter) display and read the glucose value.

Return ONLY valid JSON (no markdown, no explanation) with this exact structure:
{
    "value": the numeric glucose reading as a float,
    "unit": "mmol/L" or "mg/dL" (whichever is shown on the device),
    "value_mmol": the value converted to mmol/L (if already mmol/L, same as value; if mg/dL, divide by 18),
    "device_info": "brand/model if visible, otherwise 'unknown'",
    "confidence": "low|medium|high",
    "notes": "any relevant observations (e.g. error codes, battery low indicator, etc.)"
}

If you cannot read the display clearly, set confidence to "low".
If the image does not appear to be a glucometer, return: {"error": "No glucometer detected in image", "confidence": "low"}"""

    try:
        response = model.generate_content([
            prompt,
            {'mime_type': mime_type, 'data': image_bytes}
        ])
        result = _parse_json_response(response.text)
        if result is None:
            return {'error': 'Could not parse AI response. Please try again.'}
        return result
    except Exception as e:
        return {'error': f'AI analysis failed: {str(e)}'}


def is_ai_configured():
    """Check if the AI service is properly configured."""
    return bool(os.environ.get('GEMINI_API_KEY'))

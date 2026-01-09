"""
LLM utilities with improved Gemini-based intent classification.

Gemini is used as the PRIMARY classifier for better accuracy.
Rule-based patterns act as quick shortcuts for obvious cases.
"""

from dotenv import load_dotenv
import os

load_dotenv()

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------

# Try these models in order until one works
GEMINI_MODELS_TO_TRY = [
    "gemini-2.5-flash",
    "models/gemini-2.5-flash",
    "gemini-2.0-flash",
    "models/gemini-2.0-flash",
    "gemini-1.5-flash",
    "models/gemini-1.5-flash",
]

# These MUST correspond to existing nodes / flows
ALLOWED_INTENTS = [
    "paid",
    "disputed",
    "callback",
    "unable",
    "willing",
]

# ------------------------------------------------------------------
# Gemini integration (PRIMARY CLASSIFIER)
# ------------------------------------------------------------------

_model_cache = None
_working_model_name = None

def get_gemini_model():
    """
    Lazily initialize and cache Gemini model.
    Tries multiple model names until one works.
    """
    global _model_cache, _working_model_name
    
    if _model_cache is not None:
        return _model_cache
    
    import google.generativeai as genai

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")

    genai.configure(api_key=api_key)
    
    # Try each model until one works
    last_error = None
    for model_name in GEMINI_MODELS_TO_TRY:
        try:
            print(f"[GEMINI] Trying model: {model_name}")
            model = genai.GenerativeModel(model_name)
            
            # Test it with a simple generation
            test_response = model.generate_content(
                "Say 'ok'",
                generation_config={'max_output_tokens': 5}
            )
            
            if test_response and test_response.text:
                print(f"[GEMINI] ✅ Successfully initialized model: {model_name}")
                _model_cache = model
                _working_model_name = model_name
                return _model_cache
                
        except Exception as e:
            last_error = e
            print(f"[GEMINI] ❌ Model {model_name} failed: {str(e)[:100]}")
            continue
    
    # If all models fail, raise the last error
    raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")


def safe_get_response_text(response):
    """
    Safely extract text from Gemini response, handling all safety filter cases.
    Returns (text, was_blocked) tuple.
    """
    try:
        # Check prompt-level blocking
        if hasattr(response, 'prompt_feedback'):
            if hasattr(response.prompt_feedback, 'block_reason'):
                if response.prompt_feedback.block_reason:
                    print(f"[GEMINI] Prompt blocked: {response.prompt_feedback.block_reason}")
                    return None, True
        
        # Check if candidates exist
        if not response.candidates or len(response.candidates) == 0:
            print("[GEMINI] No candidates in response")
            return None, True
        
        candidate = response.candidates[0]
        
        # Check candidate-level blocking
        if hasattr(candidate, 'finish_reason'):
            finish_reason = candidate.finish_reason
            # Handle both enum and string formats
            finish_reason_str = None
            if hasattr(finish_reason, 'name'):
                finish_reason_str = finish_reason.name
            elif isinstance(finish_reason, str):
                finish_reason_str = finish_reason
            elif hasattr(finish_reason, '__str__'):
                finish_reason_str = str(finish_reason)
            
            if finish_reason_str:
                # Check for blocking reasons (SAFETY, RECITATION, OTHER, or dangerous_content)
                blocking_reasons = ['SAFETY', 'RECITATION', 'OTHER', 'dangerous_content']
                if any(reason in finish_reason_str.upper() for reason in blocking_reasons):
                    print(f"[GEMINI] Candidate blocked: {finish_reason_str}")
                    return None, True
        
        # Try multiple methods to get text
        text = None
        
        # Method 1: Try content.parts
        try:
            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                parts = candidate.content.parts
                if parts and len(parts) > 0:
                    text = ''.join([part.text for part in parts if hasattr(part, 'text')])
        except (KeyError, AttributeError) as e:
            print(f"[GEMINI] Error accessing content.parts: {e}")
        
        # Method 2: Try direct text access
        if not text:
            try:
                if hasattr(response, 'text') and response.text:
                    text = response.text
            except (KeyError, AttributeError, ValueError) as e:
                print(f"[GEMINI] Error accessing response.text: {e}")
        
        # Method 3: Try candidate.text
        if not text:
            try:
                if hasattr(candidate, 'text'):
                    text = candidate.text
            except (KeyError, AttributeError) as e:
                print(f"[GEMINI] Error accessing candidate.text: {e}")
        
        if text and len(text.strip()) > 0:
            return text.strip(), False
        
        print("[GEMINI] No text found in response")
        return None, True
        
    except Exception as e:
        print(f"[GEMINI] Unexpected error extracting text: {type(e).__name__} - {e}")
        return None, True


def classify_intent_with_gemini(prompt: str) -> str:
    """
    Use Gemini to intelligently classify customer intent.
    Returns one of the ALLOWED_INTENTS.
    """
    
    try:
        model = get_gemini_model()
    except Exception as e:
        print(f"Error initializing Gemini: {e}")
        return classify_intent_rule_based(prompt)

    # Simplified prompt to avoid safety filters
    llm_prompt = f"""Classify this customer response in a debt collection call.

Response: "{prompt}"

Categories (choose the best match):
- paid: Customer claims they already made payment (e.g., "I paid", "already cleared", "payment done", "transferred")
- disputed: Customer denies the debt or says it's wrong/not theirs (e.g., "never took", "not mine", "fraud", "wrong")
- callback: Customer wants to be called back later (e.g., "call me later", "busy now", "not available", "out of town")
- unable: Customer has no money/can't afford anything (e.g., "lost job", "no money", "can't afford", "struggling")
- willing: Customer wants to pay but needs options (e.g., "can't pay full", "installment", "payment plan", "will pay", "ready to pay")

Important: If customer says they want to pay but can't pay full amount, classify as "willing" (not "unable").
If customer says they already paid, classify as "paid" (not "willing").

Return ONE word only: paid, disputed, callback, unable, or willing

Classification:"""

    try:
        response = model.generate_content(
            llm_prompt,
            generation_config={
                'temperature': 0.1,
                'max_output_tokens': 10,
            },
            safety_settings={
                'HARASSMENT': 'BLOCK_NONE',
                'HATE_SPEECH': 'BLOCK_NONE',
                'SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                'DANGEROUS_CONTENT': 'BLOCK_NONE',
            }
        )
        
        text, was_blocked = safe_get_response_text(response)
        
        if was_blocked or not text:
            print("Gemini classification blocked, using rule-based fallback")
            rule_intent = classify_intent_rule_based(prompt)
            
            # If rule-based found something, use it
            if rule_intent != "unknown":
                return rule_intent
            
            # Smart fallback for blocked cases
            text_lower = prompt.lower()
            dispute_keywords = ["not right", "doesnt seem", "doesn't seem", "wrong", "mistake", "not mine", "never took", "didn't take"]
            if any(kw in text_lower for kw in dispute_keywords):
                return "disputed"
            
            # If they mention payment but can't pay full, they're willing to negotiate
            if any(phrase in text_lower for phrase in ["can't pay", "cant pay", "cannot pay", "pay", "payment"]):
                if any(phrase in text_lower for phrase in ["full", "all", "complete", "entire"]):
                    return "willing"  # Willing to pay partial/negotiate
            
            # Default to willing (most common case)
            return "willing"
        
        intent = text.strip().lower()
        
        # Validate response
        if intent in ALLOWED_INTENTS:
            return intent
        
        # Try to extract valid intent from response
        for valid_intent in ALLOWED_INTENTS:
            if valid_intent in intent:
                return valid_intent
        
        # Fallback
        print(f"Warning: Gemini returned unexpected intent '{intent}'")
        rule_intent = classify_intent_rule_based(prompt)
        return rule_intent if rule_intent != "unknown" else "disputed"
        
    except Exception as e:
        print(f"Error in Gemini classification: {e}")
        rule_intent = classify_intent_rule_based(prompt)
        
        # If rule-based found something, use it
        if rule_intent != "unknown":
            return rule_intent
        
        # Smart fallback: check for common patterns
        text_lower = prompt.lower()
        dispute_keywords = ["not right", "doesnt seem", "doesn't seem", "wrong", "mistake", "not mine", "never took", "didn't take"]
        if any(kw in text_lower for kw in dispute_keywords):
            return "disputed"
        
        # If they mention payment but can't pay full, they're willing to negotiate
        if any(phrase in text_lower for phrase in ["can't pay", "cant pay", "cannot pay", "pay", "payment"]):
            if any(phrase in text_lower for phrase in ["full", "all", "complete", "entire"]):
                return "willing"  # Willing to pay partial/negotiate
        
        # Default to willing (most common case - customer wants to work something out)
        return "willing"


# ------------------------------------------------------------------
# Rule-based intent classification (FALLBACK/SHORTCUT)
# ------------------------------------------------------------------

def classify_intent_rule_based(prompt: str) -> str:
    """
    Fast rule-based classification for obvious cases.
    Returns 'unknown' if uncertain - Gemini will handle these.
    """

    text = prompt.lower()

    # Very clear "already paid" signals
    if any(phrase in text for phrase in [
        "already paid", "already made payment", "already cleared",
        "payment done", "payment made", "payment cleared", "payment completed",
        "i paid", "i've paid", "i have paid", "i made payment", "i cleared",
        "paid last week", "paid yesterday", "paid today", "paid it",
        "made the payment", "cleared the payment", "settled the payment",
        "transferred", "transferred the amount", "sent the money",
        "payment was made", "payment is done", "already settled",
        "cleared my dues", "paid my dues", "settled my account"
    ]):
        return "paid"

    # Very clear dispute signals
    if any(phrase in text for phrase in [
        "never took", "never borrowed", "never applied", "never had",
        "haven't taken", "havent taken", "didn't take", "didnt take",
        "not my loan", "not my account", "not my debt", "not mine",
        "don't owe", "dont owe", "do not owe", "i don't owe",
        "this is wrong", "this is incorrect", "this is not mine",
        "this is not my", "this doesn't belong", "this is fraud",
        "i didn't take", "i never took", "i never borrowed",
        "doesn't seem right", "doesnt seem right", "does not seem right",
        "not right", "seems wrong", "looks wrong", "appears wrong",
        "mistake", "error", "fraud", "fraudulent", "identity theft",
        "someone else", "wrong person", "not me", "i don't know about this",
        "i never applied", "i never signed", "unauthorized", "not authorized"
    ]):
        return "disputed"

    # Very clear callback signals
    if any(phrase in text for phrase in [
        "call later", "call me later", "call back", "callback",
        "call me next week", "call me next month", "call me tomorrow",
        "call me next time", "call me some other time",
        "call you back", "call back later", "call back tomorrow",
        "next week", "next month", "tomorrow", "some other time",
        "busy now", "busy right now", "busy at the moment", "busy currently",
        "not available", "not available now", "not available right now",
        "out of town", "currently out", "away", "travelling", "traveling",
        "can't talk now", "cant talk now", "cannot talk now",
        "not a good time", "bad time", "inconvenient time",
        "later please", "please call later", "call me when convenient"
    ]):
        return "callback"

    # Very clear financial hardship signals
    if any(phrase in text for phrase in [
        "lost my job", "lost job", "no job", "unemployed", "jobless",
        "no money", "no funds", "no cash", "broke", "out of money",
        "can't afford", "cant afford", "cannot afford", "unable to afford",
        "financial crisis", "financial difficulty", "financial trouble",
        "struggling", "struggling financially", "going through tough times",
        "difficult situation", "hard time", "tough time",
        "no income", "no salary", "no earnings", "no source of income",
        "medical emergency", "family emergency", "emergency expenses"
    ]):
        return "unable"

    # Very clear willingness to pay (including partial payment willingness)
    if any(phrase in text for phrase in [
        "i want to pay", "i will pay", "i can pay", "i'd like to pay",
        "ready to pay", "willing to pay", "prepared to pay",
        "installment", "installments", "monthly payment", "monthly installments",
        "payment plan", "payemnt plan", "pay plan", "repayment plan",
        "can i pay in", "can pay in", "pay in installments", "pay in parts",
        "emi", "equated monthly installment", "monthly emi",
        "work out a plan", "work out payment", "work something out",
        "can't pay full", "cant pay full", "cannot pay full",
        "can't pay in full", "cant pay in full", "cannot pay in full",
        "can't pay the full", "cant pay the full", "cannot pay the full",
        "can't pay full amount", "cant pay full amount", "cannot pay full amount",
        "can pay partial", "can pay some", "can pay part", "can pay portion",
        "partial payment", "pay partial", "pay some", "pay part",
        "pay later", "pay next month", "pay after", "pay when",
        "let's work", "let us work", "we can work", "we can arrange",
        "interested in paying", "want to settle", "want to clear",
        "can manage", "can arrange", "can figure out", "can work something out"
    ]):
        return "willing"

    return "unknown"


# ------------------------------------------------------------------
# Unified classifier (RULES → GEMINI)
# ------------------------------------------------------------------

def classify_intent(prompt: str) -> str:
    """
    Unified intent classifier.
    
    Strategy:
    1. Try fast rule-based classification for obvious cases
    2. If uncertain (unknown), use Gemini for intelligent classification
    3. Always guarantee a valid intent is returned
    """
    
    rule_intent = classify_intent_rule_based(prompt)
    
    if rule_intent in ALLOWED_INTENTS:
        print(f"[INTENT] Rule-based: {rule_intent}")
        return rule_intent
    
    print(f"[INTENT] Using Gemini for: '{prompt[:50]}...'")
    gemini_intent = classify_intent_with_gemini(prompt)
    print(f"[INTENT] Gemini classified as: {gemini_intent}")
    
    return gemini_intent


# ------------------------------------------------------------------
# Response generation (for negotiation node)
# ------------------------------------------------------------------

def generate_negotiation_response(context: str) -> str:
    """
    Generate intelligent, conversational responses for negotiation.
    Uses a safer prompt structure to avoid safety filters.
    """
    
    try:
        model = get_gemini_model()
        
        # Simplified, safer prompt structure
        safe_prompt = f"""{context}

Respond professionally in 2-3 sentences."""
        
        response = model.generate_content(
            safe_prompt,
            generation_config={
                'temperature': 0.7,
                'max_output_tokens': 150,
            },
            safety_settings={
                'HARASSMENT': 'BLOCK_NONE',
                'HATE_SPEECH': 'BLOCK_NONE',
                'SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                'DANGEROUS_CONTENT': 'BLOCK_NONE',
            }
        )
        
        text, was_blocked = safe_get_response_text(response)
        
        if was_blocked or not text or len(text.strip()) < 20:
            print("Warning: Gemini response blocked or incomplete, using template")
            raise Exception("Blocked or incomplete response")
        
        return text
        
    except Exception as e:
        print(f"Error generating negotiation response: {e}")
        # Return None to signal fallback needed
        return None


def generate_payment_plans(outstanding_amount: float, customer_name: str) -> list:
    """
    Generate 2-3 payment plan options using Gemini.
    Falls back to rule-based plans if Gemini fails.
    """
    
    try:
        model = get_gemini_model()
        
        # Safer prompt structure
        prompt = f"""Create 2-3 payment plans for a debt of ₹{outstanding_amount:,.0f}.

Return JSON array only:
[
  {{"name": "Plan name", "description": "Details with amount and timeline"}}
]

Generate plans:"""

        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.3,
                'max_output_tokens': 500,
            },
            safety_settings={
                'HARASSMENT': 'BLOCK_NONE',
                'HATE_SPEECH': 'BLOCK_NONE',
                'SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                'DANGEROUS_CONTENT': 'BLOCK_NONE',
            }
        )
        
        text, was_blocked = safe_get_response_text(response)
        
        if was_blocked or not text:
            print("Warning: Plan generation blocked, using fallback")
            raise Exception("Response blocked")
        
        # Extract JSON
        import json
        import re
        
        json_match = re.search(r'\[\s*\{.*?\}\s*\]', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            plans = json.loads(json_str)
            
            if isinstance(plans, list) and len(plans) > 0:
                for plan in plans:
                    if 'name' not in plan or 'description' not in plan:
                        raise Exception("Invalid plan structure")
                
                print(f"[PLANS] Generated {len(plans)} payment plans")
                return plans
        
        raise Exception("Could not extract valid JSON")
        
    except Exception as e:
        print(f"Error generating payment plans: {e}")
        return generate_fallback_plans(outstanding_amount)


def generate_fallback_plans(amount: float) -> list:
    """
    Generate fallback payment plans using rule-based logic.
    """
    
    plans = []
    
    # Plan 1: Full payment with discount
    discount = int(amount * 0.05)
    plans.append({
        "name": "Immediate Settlement",
        "description": f"Pay ₹{amount - discount:,.0f} (5% discount) in full within 7 days"
    })
    
    # Plan 2: 3-month installment
    monthly_3 = int(amount / 3)
    plans.append({
        "name": "3-Month Installment",
        "description": f"Pay ₹{monthly_3:,.0f} per month for 3 months"
    })
    
    # Plan 3: 6-month installment (if amount is large enough)
    if amount > 30000:
        monthly_6 = int(amount / 6)
        plans.append({
            "name": "6-Month Installment",
            "description": f"Pay ₹{monthly_6:,.0f} per month for 6 months"
        })
    else:
        monthly_2 = int(amount / 2)
        plans.append({
            "name": "2-Month Installment",
            "description": f"Pay ₹{monthly_2:,.0f} per month for 2 months"
        })
    
    print(f"[PLANS] Using fallback plans ({len(plans)} options)")
    return plans

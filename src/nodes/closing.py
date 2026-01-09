# src/nodes/closing.py

from ..state import CallState
from ..data import save_call_record, save_dispute, save_ptp


def closing_node(state: CallState) -> dict:
    """
    End the call professionally and record outcome.
    Handles different outcomes appropriately.
    """

    # Get the final payment status (Gemini-classified)
    payment_status = state.get("payment_status", "completed")
    
    # Generate appropriate closing message based on outcome
    if payment_status == "paid":
        closing_message = (
            "Thank you for confirming your payment. "
            "We will verify this on our end and update your account. "
            "If you have any questions, please feel free to contact us. "
            "Have a good day."
        )
        outcome = "paid"
        
    elif payment_status == "disputed":
        # Save dispute record - get reason from messages if last_user_input is cleared
        dispute_reason = state.get("last_user_input")
        if not dispute_reason:
            # Find the user message that triggered the dispute (usually after disclosure)
            messages = state.get("messages", [])
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    dispute_reason = msg.get("content", "Customer disputes the debt")
                    break
        if not dispute_reason:
            dispute_reason = "Customer disputes the debt"
        
        dispute_id = save_dispute(state["customer_id"], dispute_reason)
        
        closing_message = (
            "I understand you're disputing this debt. "
            f"I've created a dispute ticket (Reference: {dispute_id}). "
            "Our disputes team will review this and contact you within 3-5 business days. "
            "Thank you for bringing this to our attention."
        )
        outcome = "disputed"
        state["dispute_id"] = dispute_id
        state["dispute_reason"] = dispute_reason
        
    elif payment_status == "callback":
        closing_message = (
            "No problem, I understand you need more time. "
            "We'll call you back as requested. "
            "Thank you for your time today."
        )
        outcome = "callback"
        
    elif payment_status == "unable":
        closing_message = (
            "I understand your current financial situation. "
            "Our team will review your case and contact you to discuss possible options. "
            "Thank you for being honest with us today."
        )
        outcome = "unable"
        
    elif payment_status == "willing":
        # Check if PTP was already recorded in negotiation node
        if state.get("ptp_id"):
            # PTP already saved in negotiation node
            ptp_id = state.get("ptp_id")
            ptp_amount = state.get("ptp_amount")
            ptp_date = state.get("ptp_date")
            plan_name = state.get("selected_plan", {}).get("name", "Payment Plan") if state.get("selected_plan") else "Payment Plan"
            
            closing_message = (
                f"Perfect! I've documented your commitment to the {plan_name} "
                f"with payment of ₹{ptp_amount:,.0f} starting on {ptp_date}. "
                f"Your PTP reference number is {ptp_id}. "
                f"You'll receive a confirmation shortly. Thank you for working this out with us. Have a great day!"
            )
            outcome = "ptp_recorded"
        else:
            # Customer discussed payment but no specific commitment yet
            closing_message = (
                "Thank you for discussing this with us today. "
                "Based on our conversation, we'll follow up with you shortly to finalize the payment arrangement. "
                "If you'd like to proceed with payment before then, please contact us. "
                "Have a good day."
            )
            outcome = "willing"
        
    else:
        # Fallback for any unexpected status
        closing_message = (
            "Thank you for your time today. "
            "If you have any questions, please feel free to contact us. "
            "Have a good day."
        )
        outcome = payment_status or "completed"

    # Create call summary
    summary = f"""
Call completed.
Verified: {state['is_verified']}
Outcome: {outcome}
Payment Status: {payment_status}
Customer: {state['customer_name']}
Outstanding Amount: ₹{state['outstanding_amount']}
"""

    # Save call record
    save_call_record({
        "customer_id": state["customer_id"],
        "outcome": outcome,
        "payment_status": payment_status,
        "summary": summary.strip()
    })

    return {
        "messages": state["messages"] + [{
            "role": "assistant",
            "content": closing_message
        }],
        "call_outcome": outcome,
        "call_summary": summary.strip(),
        "is_complete": True,
        "stage": "closing",
    }
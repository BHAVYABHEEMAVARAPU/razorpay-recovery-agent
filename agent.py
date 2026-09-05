from typing import Dict, Any, List
from engine import evaluate_recovery


# =========================================================
# REVENSIGHT RECOVERY AGENT
# =========================================================

class RecoveryAgent:

    def __init__(self, transactions, customers):

        self.transactions = transactions
        self.customers = customers

        self.audit_log: List[Dict[str, Any]] = []

    # -----------------------------------------------------
    # TOOL 1: GET CUSTOMER HISTORY
    # -----------------------------------------------------

    def get_customer_history(
        self,
        customer_id: str
    ) -> Dict[str, Any]:

        customer = self.customers.get(
            customer_id,
            {
                "successful_payments": 0,
                "previous_failures": 0,
                "lifetime_value": 0
            }
        )

        self.audit_log.append({
            "tool": "get_customer_history",
            "customer_id": customer_id
        })

        return customer

    # -----------------------------------------------------
    # TOOL 2: DIAGNOSE + DECIDE
    # -----------------------------------------------------

    def diagnose_transaction(
        self,
        transaction: Dict[str, Any]
    ) -> Dict[str, Any]:

        customer_id = transaction.get(
            "customer_id"
        )

        customer = self.get_customer_history(
            customer_id
        )

        result = evaluate_recovery(
            transaction,
            customer
        )

        self.audit_log.append({
            "tool": "recovery_decision",
            "transaction_id": transaction.get(
                "transaction_id"
            ),
            "decision": result["decision"]
        })

        return result

    # -----------------------------------------------------
    # TOOL 3: EXECUTE CONTROLLED ACTION
    # -----------------------------------------------------

    def execute_action(
        self,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:

        action = result["decision"]

        # IMPORTANT:
        # This is a simulation layer.
        # It does NOT move real money.

        if action == "RETRY_NOW":

            execution = {
                "status": "SIMULATED_RETRY",
                "message": "Retry action queued in sandbox simulation."
            }

        elif action == "SCHEDULE_RETRY":

            execution = {
                "status": "SIMULATED_SCHEDULE",
                "message": "Future retry scheduled in sandbox simulation."
            }

        elif action == "SEND_PAYMENT_LINK":

            execution = {
                "status": "SIMULATED_MESSAGE",
                "message": "Customer recovery message generated."
            }

        elif action == "ESCALATE":

            execution = {
                "status": "ESCALATED",
                "message": "Transaction sent to merchant review."
            }

        else:

            execution = {
                "status": "STOPPED",
                "message": "Automatic recovery stopped."
            }

        self.audit_log.append({
            "tool": "execute_recovery_action",
            "transaction_id": result.get(
                "transaction_id"
            ),
            "action": action,
            "execution": execution["status"]
        })

        return execution

    # -----------------------------------------------------
    # TOOL 4: RUN SINGLE TRANSACTION
    # -----------------------------------------------------

    def run_transaction(
        self,
        transaction: Dict[str, Any]
    ) -> Dict[str, Any]:

        result = self.diagnose_transaction(
            transaction
        )

        execution = self.execute_action(
            result
        )

        result["execution"] = execution

        return result

    # -----------------------------------------------------
    # RUN COMPLETE BATCH
    # -----------------------------------------------------

    def run(self) -> Dict[str, Any]:

        results = []

        for transaction in self.transactions:

            result = self.run_transaction(
                transaction
            )

            results.append(result)

        return {
            "results": results,
            "agent_audit_log": self.audit_log
        }
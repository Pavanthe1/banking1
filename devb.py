# LoanProcessingSystem.py

from dataclasses import dataclass


@dataclass
class LoanApplication:
    customer_id: str
    age: int
    monthly_salary: float
    existing_loan_amount: float
    credit_score: int
    employment_type: str
    requested_loan_amount: float
    loan_tenure_years: int


class LoanProcessingSystem:

    MIN_AGE = 21
    MAX_AGE = 60
    MIN_SALARY = 10000.0
    MIN_CREDIT_SCORE = 300
    MAX_CREDIT_SCORE = 900
    MAX_DTI_RATIO = 0.40
    MAX_EXISTING_LOAN_RATIO = 0.50
    MIN_LOAN_AMOUNT = 50000.0
    MAX_LOAN_AMOUNT = 5000000.0
    MIN_TENURE = 1
    MAX_TENURE = 30

    EMPLOYMENT_MULTIPLIERS = {
        "salaried": 20,
        "self-employed": 15,
        "government": 25,
        "contract": 10
    }

    def validate(self, application):
        if not application.customer_id.strip():
            raise ValueError("Customer ID cannot be empty.")

        if not self.MIN_AGE <= application.age <= self.MAX_AGE:
            raise ValueError("Age must be between 21 and 60.")

        if application.monthly_salary < self.MIN_SALARY:
            raise ValueError("Monthly salary must be at least 10000.")

        if application.existing_loan_amount < 0:
            raise ValueError("Existing loan amount cannot be negative.")

        if not self.MIN_CREDIT_SCORE <= application.credit_score <= self.MAX_CREDIT_SCORE:
            raise ValueError("Credit score must be between 300 and 900.")

        if application.employment_type.lower() not in self.EMPLOYMENT_MULTIPLIERS:
            raise ValueError("Invalid employment type.")

        if not self.MIN_LOAN_AMOUNT <= application.requested_loan_amount <= self.MAX_LOAN_AMOUNT:
            raise ValueError("Requested loan must be between 50000 and 5000000.")

        if not self.MIN_TENURE <= application.loan_tenure_years <= self.MAX_TENURE:
            raise ValueError("Loan tenure must be between 1 and 30 years.")

    @staticmethod
    def calculate_emi(principal, annual_interest_rate, tenure_years):
        if principal < 0:
            raise ValueError("Principal cannot be negative.")
        if annual_interest_rate < 0:
            raise ValueError("Interest rate cannot be negative.")
        if tenure_years <= 0:
            raise ValueError("Tenure must be positive.")
        if principal == 0:
            return 0.0

        months = tenure_years * 12
        monthly_rate = annual_interest_rate / 1200

        if monthly_rate == 0:
            return principal / months

        factor = (1 + monthly_rate) ** months
        return principal * monthly_rate * factor / (factor - 1)

    def process_loan(self, application):
        self.validate(application)

        salary = application.monthly_salary
        existing_loan = application.existing_loan_amount
        credit_score = application.credit_score
        employment = application.employment_type.lower()
        tenure = application.loan_tenure_years

        dti_ratio = (existing_loan / salary) if salary else float("inf")

        eligible_amount = salary * self.EMPLOYMENT_MULTIPLIERS[employment] * 12
        eligible_amount = min(eligible_amount, self.MAX_LOAN_AMOUNT)

        if credit_score < 600:
            interest_rate = 16.0
        elif credit_score < 700:
            interest_rate = 12.0
        elif credit_score < 800:
            interest_rate = 9.0
        else:
            interest_rate = 7.0

        if employment == "contract":
            interest_rate += 2.0
        elif employment == "self-employed":
            interest_rate += 1.0

        monthly_capacity = salary * self.MAX_DTI_RATIO
        maximum_supported_principal = (
            monthly_capacity * tenure * 12
            if interest_rate == 0
            else monthly_capacity
            * (1 - (1 + interest_rate / 1200) ** (-tenure * 12))
            / (interest_rate / 1200)
        )

        eligible_amount = min(
            eligible_amount,
            maximum_supported_principal
        )

        emi = self.calculate_emi(
            application.requested_loan_amount,
            interest_rate,
            tenure
        )

        approval = (
            credit_score >= 600
            and dti_ratio <= self.MAX_EXISTING_LOAN_RATIO
            and application.requested_loan_amount <= eligible_amount
            and emi + existing_loan <= monthly_capacity
        )

        return {
            "customer_id": application.customer_id,
            "debt_to_income_ratio": round(dti_ratio * 100, 2),
            "eligible_loan_amount": round(max(0, eligible_amount), 2),
            "interest_rate": round(interest_rate, 2),
            "emi": round(emi, 2),
            "status": "APPROVED" if approval else "REJECTED"
        }


def main():
    system = LoanProcessingSystem()

    try:
        application = LoanApplication(
            customer_id=input("Customer ID: ").strip(),
            age=int(input("Age: ")),
            monthly_salary=float(input("Monthly salary: ")),
            existing_loan_amount=float(input("Existing loan amount: ")),
            credit_score=int(input("Credit score (300-900): ")),
            employment_type=input(
                "Employment (salaried/self-employed/government/contract): "
            ).strip(),
            requested_loan_amount=float(input("Requested loan amount: ")),
            loan_tenure_years=int(input("Loan tenure in years: "))
        )

        result = system.process_loan(application)

        for key, value in result.items():
            print(f"{key}: {value}")

    except (ValueError, TypeError) as error:
        print(f"Invalid application: {error}")
    except Exception as error:
        print(f"Unexpected error: {error}")


if __name__ == "__main__":
    main()

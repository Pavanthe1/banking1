
class LoanProcessingSystem:

    MIN_AGE = 21
    MAX_AGE = 60
    MIN_SALARY = 10000
    MIN_CREDIT_SCORE = 300
    MAX_CREDIT_SCORE = 900
    MIN_LOAN = 50000
    MAX_LOAN = 5000000

    EMPLOYMENT_MULTIPLIERS = {
        "salaried": 20,
        "self-employed": 15,
        "government": 25,
        "contract": 10
    }

    def validate(self, app):
        required = [
            "customer_id", "age", "monthly_salary",
            "existing_loan_amount", "credit_score",
            "employment_type", "requested_loan_amount",
            "loan_tenure_years"
        ]

        if not isinstance(app, dict):
            raise ValueError("Application must be a dictionary")

        for key in required:
            if key not in app:
                raise ValueError(f"Missing field: {key}")

        if not isinstance(app["customer_id"], str) or not app["customer_id"].strip():
            raise ValueError("Invalid customer ID")

        if type(app["age"]) is not int or not self.MIN_AGE <= app["age"] <= self.MAX_AGE:
            raise ValueError("Age must be between 21 and 60")

        salary = app["monthly_salary"]
        if type(salary) not in (int, float) or salary < self.MIN_SALARY:
            raise ValueError("Monthly salary must be at least 10000")

        existing = app["existing_loan_amount"]
        if type(existing) not in (int, float) or existing < 0:
            raise ValueError("Invalid existing loan amount")

        score = app["credit_score"]
        if type(score) is not int or not self.MIN_CREDIT_SCORE <= score <= self.MAX_CREDIT_SCORE:
            raise ValueError("Credit score must be between 300 and 900")

        employment = app["employment_type"]
        if not isinstance(employment, str) or employment.lower() not in self.EMPLOYMENT_MULTIPLIERS:
            raise ValueError("Invalid employment type")

        requested = app["requested_loan_amount"]
        if type(requested) not in (int, float) or not self.MIN_LOAN <= requested <= self.MAX_LOAN:
            raise ValueError("Loan amount must be between 50000 and 5000000")

        tenure = app["loan_tenure_years"]
        if type(tenure) is not int or not 1 <= tenure <= 30:
            raise ValueError("Tenure must be between 1 and 30 years")

    @staticmethod
    def calculate_emi(principal, annual_rate, years):
        if principal < 0 or annual_rate < 0 or years <= 0:
            raise ValueError("Invalid EMI input")

        months = years * 12

        if principal == 0:
            return 0.0

        rate = annual_rate / 1200

        if rate == 0:
            return principal / months

        factor = (1 + rate) ** months
        return principal * rate * factor / (factor - 1)

    def process_loan(self, app):
        self.validate(app)

        salary = app["monthly_salary"]
        existing = app["existing_loan_amount"]
        score = app["credit_score"]
        employment = app["employment_type"].lower()
        requested = app["requested_loan_amount"]
        years = app["loan_tenure_years"]

        dti = existing / salary * 100

        if score < 600:
            interest = 16.0
        elif score < 700:
            interest = 12.0
        elif score < 800:
            interest = 9.0
        else:
            interest = 7.0

        if employment == "contract":
            interest += 2
        elif employment == "self-employed":
            interest += 1

        eligible = min(
            salary * self.EMPLOYMENT_MULTIPLIERS[employment] * 12,
            self.MAX_LOAN
        )

        monthly_capacity = salary * 0.40
        monthly_rate = interest / 1200
        months = years * 12

        supported_amount = monthly_capacity * (
            (1 - (1 + monthly_rate) ** (-months)) / monthly_rate
        )

        eligible = min(eligible, supported_amount)

        emi = self.calculate_emi(requested, interest, years)

        approved = (
            score >= 600
            and dti <= 50
            and requested <= eligible
            and emi + existing <= monthly_capacity
        )

        return {
            "customer_id": app["customer_id"],
            "debt_to_income_ratio": round(dti, 2),
            "eligible_loan_amount": round(max(0, eligible), 2),
            "interest_rate": round(interest, 2),
            "emi": round(emi, 2),
            "status": "APPROVED" if approved else "REJECTED"
        }


def main():
    system = LoanProcessingSystem()

    try:
        application = {
            "customer_id": input("Customer ID: ").strip(),
            "age": int(input("Age: ")),
            "monthly_salary": float(input("Monthly salary: ")),
            "existing_loan_amount": float(input("Existing loan amount: ")),
            "credit_score": int(input("Credit score: ")),
            "employment_type": input(
                "Employment type (salaried/self-employed/government/contract): "
            ).strip(),
            "requested_loan_amount": float(input("Requested loan amount: ")),
            "loan_tenure_years": int(input("Loan tenure in years: "))
        }

        result = system.process_loan(application)

        for key, value in result.items():
            print(f"{key}: {value}")

    except (ValueError, TypeError) as error:
        print("Application error:", error)
    except Exception as error:
        print("Unexpected error:", error)


if __name__ == "__main__":
    main()

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
        if not isinstance(app["customer_id"], str) or not app["customer_id"].strip():
            raise ValueError("Invalid customer ID")

        if not isinstance(app["age"], int) or not self.MIN_AGE <= app["age"] <= self.MAX_AGE:
            raise ValueError("Age must be between 21 and 60")

        if not isinstance(app["monthly_salary"], (int, float)) or isinstance(app["monthly_salary"], bool) or app["monthly_salary"] < self.MIN_SALARY:
            raise ValueError("Invalid monthly salary")

        if not isinstance(app["existing_loan_amount"], (int, float)) or isinstance(app["existing_loan_amount"], bool) or app["existing_loan_amount"] < 0:
            raise ValueError("Invalid existing loan amount")

        if not isinstance(app["credit_score"], int) or not self.MIN_CREDIT_SCORE <= app["credit_score"] <= self.MAX_CREDIT_SCORE:
            raise ValueError("Credit score must be between 300 and 900")

        if not isinstance(app["employment_type"], str) or app["employment_type"].lower() not in self.EMPLOYMENT_MULTIPLIERS:
            raise ValueError("Invalid employment type")

        if not isinstance(app["requested_loan_amount"], (int, float)) or isinstance(app["requested_loan_amount"], bool) or not self.MIN_LOAN <= app["requested_loan_amount"] <= self.MAX_LOAN:
            raise ValueError("Loan amount must be between 50000 and 5000000")

        if not isinstance(app["loan_tenure_years"], int) or not 1 <= app["loan_tenure_years"] <= 30:
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


if __name__ == "__main__":
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

import unittest

from LoanProcessingSystem import LoanProcessingSystem


class LoanProcessingQA(unittest.TestCase):

    def setUp(self):
        self.system = LoanProcessingSystem()

    def valid_app(self, **changes):
        app = {
            "customer_id": "C1001",
            "age": 30,
            "monthly_salary": 100000,
            "existing_loan_amount": 5000,
            "credit_score": 800,
            "employment_type": "salaried",
            "requested_loan_amount": 500000,
            "loan_tenure_years": 10
        }
        app.update(changes)
        return app

    def test_valid_application(self):
        result = self.system.process_loan(self.valid_app())
        self.assertEqual(result["status"], "APPROVED")

    def test_minimum_age(self):
        self.system.process_loan(self.valid_app(age=21))

    def test_maximum_age(self):
        self.system.process_loan(self.valid_app(age=60))

    def test_age_below_minimum(self):
        with self.assertRaises(ValueError):
            self.system.process_loan(self.valid_app(age=20))

    def test_age_above_maximum(self):
        with self.assertRaises(ValueError):
            self.system.process_loan(self.valid_app(age=61))

    def test_invalid_salary(self):
        for salary in (0, -1000, "invalid", None):
            with self.subTest(salary=salary):
                with self.assertRaises(ValueError):
                    self.system.process_loan(
                        self.valid_app(monthly_salary=salary)
                    )

    def test_poor_credit_score(self):
        result = self.system.process_loan(
            self.valid_app(credit_score=500)
        )
        self.assertEqual(result["status"], "REJECTED")

    def test_credit_score_boundaries(self):
        for score in (300, 600, 700, 800, 900):
            with self.subTest(score=score):
                result = self.system.process_loan(
                    self.valid_app(credit_score=score)
                )
                self.assertIn(result["status"], ("APPROVED", "REJECTED"))

    def test_invalid_credit_score(self):
        for score in (299, 901, None):
            with self.subTest(score=score):
                with self.assertRaises(ValueError):
                    self.system.process_loan(
                        self.valid_app(credit_score=score)
                    )

    def test_existing_loan_exceeds_threshold(self):
        result = self.system.process_loan(
            self.valid_app(existing_loan_amount=60000)
        )
        self.assertEqual(result["status"], "REJECTED")

    def test_negative_existing_loan(self):
        with self.assertRaises(ValueError):
            self.system.process_loan(
                self.valid_app(existing_loan_amount=-1)
            )

    def test_high_debt_to_income_ratio(self):
        result = self.system.process_loan(
            self.valid_app(
                monthly_salary=20000,
                existing_loan_amount=15000
            )
        )
        self.assertGreater(result["debt_to_income_ratio"], 50)
        self.assertEqual(result["status"], "REJECTED")

    def test_employment_categories(self):
        for category in (
            "salaried", "self-employed", "government", "contract"
        ):
            with self.subTest(category=category):
                result = self.system.process_loan(
                    self.valid_app(employment_type=category)
                )
                self.assertIn(result["status"], ("APPROVED", "REJECTED"))

    def test_invalid_employment(self):
        with self.assertRaises(ValueError):
            self.system.process_loan(
                self.valid_app(employment_type="unemployed")
            )

    def test_minimum_loan_amount(self):
        self.system.process_loan(
            self.valid_app(requested_loan_amount=50000)
        )

    def test_maximum_loan_amount(self):
        result = self.system.process_loan(
            self.valid_app(requested_loan_amount=5000000)
        )
        self.assertEqual(result["status"], "REJECTED")

    def test_loan_below_minimum(self):
        with self.assertRaises(ValueError):
            self.system.process_loan(
                self.valid_app(requested_loan_amount=49999)
            )

    def test_loan_above_maximum(self):
        with self.assertRaises(ValueError):
            self.system.process_loan(
                self.valid_app(requested_loan_amount=5000001)
            )

    def test_emi_accuracy(self):
        emi = self.system.calculate_emi(100000, 12, 1)
        self.assertAlmostEqual(emi, 8884.88, delta=0.02)

    def test_zero_interest_emi(self):
        emi = self.system.calculate_emi(120000, 0, 1)
        self.assertAlmostEqual(emi, 10000, places=2)

    def test_zero_principal_emi(self):
        self.assertEqual(self.system.calculate_emi(0, 12, 1), 0)

    def test_negative_principal(self):
        with self.assertRaises(ValueError):
            self.system.calculate_emi(-1000, 12, 1)

    def test_negative_interest(self):
        with self.assertRaises(ValueError):
            self.system.calculate_emi(1000, -1, 1)

    def test_invalid_tenure(self):
        with self.assertRaises(ValueError):
            self.system.calculate_emi(1000, 12, 0)

    def test_invalid_application_tenure(self):
        for tenure in (0, 31, None):
            with self.subTest(tenure=tenure):
                with self.assertRaises(ValueError):
                    self.system.process_loan(
                        self.valid_app(loan_tenure_years=tenure)
                    )

    def test_empty_customer_id(self):
        with self.assertRaises(ValueError):
            self.system.process_loan(
                self.valid_app(customer_id="")
            )

    def test_null_customer_id(self):
        with self.assertRaises(ValueError):
            self.system.process_loan(
                self.valid_app(customer_id=None)
            )

    def test_non_string_employment(self):
        with self.assertRaises(ValueError):
            self.system.process_loan(
                self.valid_app(employment_type=None)
            )

    def test_invalid_numeric_type(self):
        with self.assertRaises(ValueError):
            self.system.process_loan(
                self.valid_app(monthly_salary="invalid")
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)

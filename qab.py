# LoanProcessingQA.py

import unittest

from LoanProcessingSystem import LoanApplication, LoanProcessingSystem


class LoanProcessingQA(unittest.TestCase):

    def setUp(self):
        self.system = LoanProcessingSystem()

    def valid_application(self, **overrides):
        values = {
            "customer_id": "C1001",
            "age": 30,
            "monthly_salary": 100000.0,
            "existing_loan_amount": 5000.0,
            "credit_score": 800,
            "employment_type": "salaried",
            "requested_loan_amount": 500000.0,
            "loan_tenure_years": 10
        }
        values.update(overrides)
        return LoanApplication(**values)

    def test_valid_loan_approval(self):
        result = self.system.process_loan(self.valid_application())
        self.assertEqual(result["status"], "APPROVED")

    def test_minimum_age(self):
        result = self.system.process_loan(
            self.valid_application(age=21)
        )
        self.assertIn(result["status"], ["APPROVED", "REJECTED"])

    def test_maximum_age(self):
        result = self.system.process_loan(
            self.valid_application(age=60)
        )
        self.assertIn(result["status"], ["APPROVED", "REJECTED"])

    def test_age_below_minimum(self):
        with self.assertRaises(ValueError):
            self.system.process_loan(
                self.valid_application(age=20)
            )

    def test_age_above_maximum(self):
        with self.assertRaises(ValueError):
            self.system.process_loan(
                self.valid_application(age=61)
            )

    def test_invalid_salary_zero(self):
        with self.assertRaises(ValueError):
            self.system.process_loan(
                self.valid_application(monthly_salary=0)
            )

    def test_invalid_negative_salary(self):
        with self.assertRaises(ValueError):
            self.system.process_loan(
                self.valid_application(monthly_salary=-1000)
            )

    def test_poor_credit_score(self):
        result = self.system.process_loan(
            self.valid_application(credit_score=500)
        )
        self.assertEqual(result["status"], "REJECTED")

    def test_minimum_credit_score(self):
        result = self.system.process_loan(
            self.valid_application(credit_score=300)
        )
        self.assertEqual(result["status"], "REJECTED")

    def test_maximum_credit_score(self):
        result = self.system.process_loan(
            self.valid_application(credit_score=900)
        )
        self.assertEqual(result["status"], "APPROVED")

    def test_credit_score_below_range(self):
        with self.assertRaises(ValueError):
            self.system.process_loan(
                self.valid_application(credit_score=299)
            )

    def test_credit_score_above_range(self):
        with self.assertRaises(ValueError):
            self.system.process_loan(
                self.valid_application(credit_score=901)
            )

    def test_existing_loan_exceeds_threshold(self):
        result = self.system.process_loan(
            self.valid_application(existing_loan_amount=60000)
        )
        self.assertEqual(result["status"], "REJECTED")

    def test_high_debt_to_income_ratio(self):
        result = self.system.process_loan(
            self.valid_application(
                monthly_salary=20000,
                existing_loan_amount=15000
            )
        )
        self.assertGreater(result["debt_to_income_ratio"], 40)
        self.assertEqual(result["status"], "REJECTED")

    def test_all_employment_categories(self):
        categories = [
            "salaried",
            "self-employed",
            "government",
            "contract"
        ]

        for category in categories:
            with self.subTest(employment_type=category):
                result = self.system.process_loan(
                    self.valid_application(employment_type=category)
                )
                self.assertIn(result["status"], ["APPROVED", "REJECTED"])

    def test_invalid_employment_category(self):
        with self.assertRaises(ValueError):
            self.system.process_loan(
                self.valid_application(employment_type="unemployed")
            )

    def test_minimum_loan_amount(self):
        result = self.system.process_loan(
            self.valid_application(requested_loan_amount=50000)
        )
        self.assertIn(result["status"], ["APPROVED", "REJECTED"])

    def test_maximum_loan_amount(self):
        result = self.system.process_loan(
            self.valid_application(requested_loan_amount=5000000)
        )
        self.assertEqual(result["status"], "REJECTED")

    def test_loan_amount_below_minimum(self):
        with self.assertRaises(ValueError):
            self.system.process_loan(
                self.valid_application(requested_loan_amount=49999)
            )

    def test_loan_amount_above_maximum(self):
        with self.assertRaises(ValueError):
            self.system.process_loan(
                self.valid_application(requested_loan_amount=5000001)
            )

    def test_emi_calculation_accuracy(self):
        emi = self.system.calculate_emi(100000, 12, 1)
        self.assertAlmostEqual(emi, 8884.88, delta=0.02)

    def test_zero_interest_emi(self):
        emi = self.system.calculate_emi(120000, 0, 1)
        self.assertAlmostEqual(emi, 10000.00, places=2)

    def test_zero_principal_emi(self):
        self.assertEqual(
            self.system.calculate_emi(0, 12, 1),
            0.0
        )

    def test_negative_principal_exception(self):
        with self.assertRaises(ValueError):
            self.system.calculate_emi(-1000, 12, 1)

    def test_negative_interest_exception(self):
        with self.assertRaises(ValueError):
            self.system.calculate_emi(1000, -1, 1)

    def test_invalid_tenure_exception(self):
        with self.assertRaises(ValueError):
            self.system.calculate_emi(1000, 12, 0)

    def test_invalid_loan_tenure(self):
        with self.assertRaises(ValueError):
            self.system.process_loan(
                self.valid_application(loan_tenure_years=31)
            )

    def test_negative_existing_loan(self):
        with self.assertRaises(ValueError):
            self.system.process_loan(
                self.valid_application(existing_loan_amount=-1)
            )

    def test_empty_customer_id(self):
        with self.assertRaises(ValueError):
            self.system.process_loan(
                self.valid_application(customer_id="")
            )

    def test_invalid_numeric_input_handling(self):
        with self.assertRaises((ValueError, TypeError)):
            self.system.process_loan(
                self.valid_application(monthly_salary="invalid")
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)

import unittest

from peewee import IntegrityError
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains


import flask_journal
import models

# test models and views separately.


class test_AA_Meta(unittest.TestCase):
    def test_AA_import(self):
        def import_failure_proof(self):
            with self.assertRaises(NameError):
                # PEP8 error is intentional here
                (batmans_secret_identity.__name__ is 'Bruce Wayne')
                # if we import a file, we'll get a name error
                # if it can't be imported and we call __name__ on it

        def test_main(self):
            self.assertEqual(self.__name__ == "__main__")


# ### MODELS ### #
class test_A_Models(unittest.TestCase):
    def test_A_models_A0_import(self):
        self.assertEqual(
            # won't work if the import failed
            models.__name__,
            'models'
        )

    def test_A_models_AAA_debug(self):
        self.assertTrue(models.DEBUG)

    def test_A_models_AA_db(self):
        self.assertEqual(models.DATABASE.database, 'TESTING_flask_journal.db')

    def test_A_models_A_BaseModel(self):
        '''nothing special yet, just making sure it loads
will throw a NameError if it doesn't
'''
        basemodel = models.BaseModel()
        # and is empty
        # with self.assertRaises(AttributeError):
        print(basemodel.__data__)

    def test_A_models_A_Entry(self):
        entry = models.Entry()
        self.assertEqual(entry.title, None)

    def test_A_models_B_Entry_create(self):
        tries = 0
        timeout_limit = 5
        while tries < timeout_limit:
            try:
                entry = models.Entry.create_entry(
                    # Title
                    title='Test Entry',
                    # Date
                    date='2018-07-03',
                    # Time Spent
                    time_spent=9001,
                    # What You Learned
                    learned="I learned a lot about unittesting!",
                    # Resources to Remember
                    resources="https://www.python.org/dev/peps/pep-0484/",
                )
                # if we tried more than once
                #   if tries:
                #       pass
                self.assertTrue(entry.title == 'Test Entry')
                return True

            # a task called 'Test Entry' already exists from a prior test
            except IntegrityError:
                # delete the task called 'Test Entry'
                models.Entry.get_entry_from_slug('test-entry').delete_entry()
                # try again (loop repeats, up to 5 times)
                tries += 1

    def test_A_models_D_Entry_edit(self):

        # doesn't matter, we're gonna edit em anyway
        entry = models.Entry.get()
        # but we want to keep track of which one
        entry_id = entry.id

        # title
        entry.edit(title='Test Entry (Edited)')
        self.assertEqual(entry.title, 'Test Entry (Edited)')
        self.assertEqual(entry.slugify_title(), 'test-entry-edited')

        # make sure if we call an entry by the slug, the right one comes up
        self.assertEqual(
            models.Entry.get_entry_from_slug('test-entry-edited').id,
            entry_id
            )

        # date
        entry.edit(date='1985-7-3')
        self.assertEqual(entry.get_datetime_string(), '1985-07-03')
        self.assertEqual(entry.get_date_string(), 'July 03, 1985')

        # time spent
        entry.edit(time_spent=20)
        self.assertEqual(entry.display_time_spent(), '20 minutes')
        entry.edit(time_spent=240)
        self.assertEqual(entry.display_time_spent(), '4.0 hours')
        entry.edit(time_spent=48*60)
        self.assertEqual(entry.display_time_spent(), '2.0 days')
        entry.edit(time_spent=60*24*7*2)
        self.assertEqual(entry.display_time_spent(), '2.0 weeks')
        entry.edit(time_spent=12*31*24*60)
        self.assertEqual(entry.display_time_spent(), '1.018501793900169 years')

        # learned
        entry.edit(learned="the more I know the less i understand")
        self.assertIn('understand', entry.learned)

        # resources
        entry.edit(resources=(
            'Capitalism does not permit an even flow of economic resources'))
        self.assertIn('economic resources', entry.resources)

    def test_A_models_Z_Entry_delete(self):
        # doesn't matter, we're seeing that it deletes
        entry = models.Entry.get()
        entry.delete_entry()


def mouseToAndClick(element):
    ActionChains(driver).move_to_element(element).click(
        element).perform()


# test models and views separately.
class test_B_views(unittest.TestCase):

    def test_B_import(self):
        self.assertEqual(
            # won't work if the import failed
            flask_journal.__name__,
            'flask_journal'
        )


class selenium_login(unittest.TestCase):
    def test_C_user_login(self):
        driver.get(ENVIRONMENTS['Debug']+'login')
        username_field = driver.find_element_by_css_selector(
            '#username')
        password_field = driver.find_element_by_css_selector(
            '#password')
        submit_button = driver.find_element_by_css_selector(
            '#submit')
        username_field.clear()
        mouseToAndClick(username_field)
        username_field.send_keys(
            'Mhunterak')
        password_field.clear()
        mouseToAndClick(password_field)
        password_field.send_keys(
            'password')
        mouseToAndClick(submit_button)

        self.assertTrue(driver.find_element_by_css_selector(
            '.flashes').is_displayed())

        logout_button = driver.find_element_by_xpath(
            "//*[contains(text(), 'Log Out')]")

        self.assertTrue(logout_button.is_displayed())
        mouseToAndClick(logout_button)


ENVIRONMENTS = {
        'Debug': (
            'http://local:8000/'),
        # 'Alpha': 'none',
        # 'Beta': 'none',
        # 'Production': 'none',
    }
BROWSERS = {
    'Chrome': webdriver.Chrome(),
    # 'Firefox': webdriver.Firefox()
    }
for browser in BROWSERS.keys():
    driver = BROWSERS[browser]
    BROWSER = browser

    suite = unittest.TestLoader().loadTestsFromTestCase(selenium_login)
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':  # pragma: no cover
    unittest.main(verbosity=2)

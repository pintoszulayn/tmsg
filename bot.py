#!/usr/bin/env python3
"""Ticketmaster Bot Core Logic

This module contains the core functionality of the Ticketmaster Bot,
including queue bypassing, ticket selection, captcha solving, and checkout.
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from twocaptcha import TwoCaptcha
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TicketmasterBot:
    """A bot to automate ticket purchasing on Ticketmaster.sg."""

    def __init__(self, url, proxy=None, captcha_key=None, card_number=None, expiry=None, cvc=None):
        """Initialize the bot with user-provided parameters."""
        self.url = url
        self.proxy = proxy
        self.captcha_key = captcha_key
        self.card_number = card_number
        self.expiry = expiry
        self.cvc = cvc
        self.driver = self._setup_driver()
        self.captcha_solver = TwoCaptcha(captcha_key) if captcha_key else None

    def _setup_driver(self):
        """Set up the Chrome WebDriver with custom options."""
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.{random.randint(100, 999)} Safari/537.36")
        if self.proxy:
            chrome_options.add_argument(f'--proxy-server={self.proxy}')
        return webdriver.Chrome(options=chrome_options)

    def check_queue(self):
        """Check if the current page is a queue page."""
        try:
            wait = WebDriverWait(self.driver, 10)
            queue_indicators = [
                (By.ID, "queue-it"),
                (By.CLASS_NAME, "queue-it-container"),
                (By.XPATH, "//div[contains(text(), 'Waiting Room')]")
            ]
            for locator in queue_indicators:
                wait.until(EC.presence_of_element_located(locator))
                logger.info(f"Detected queue page via {locator}, current URL: {self.driver.current_url}")
                return True
        except:
            if "queue" in self.driver.current_url.lower():
                logger.info(f"Detected queue via URL: {self.driver.current_url}")
                return True
            logger.info(f"No queue detected, current URL: {self.driver.current_url}")
            return False

    def bypass_queue(self):
        """Attempt to bypass the queue by navigating to the purchase page."""
        possible_urls = [
            self.url + "/buy",
            self.url + "/tickets",
            self.url.replace("activity/detail", "tickets")
        ]
        for bypass_url in possible_urls:
            logger.info(f"Attempting to bypass queue, navigating to: {bypass_url}")
            self.driver.get(bypass_url)
            time.sleep(2)
            if "queue" not in self.driver.current_url.lower():
                logger.info(f"Bypass successful, current URL: {self.driver.current_url}")
                return
        logger.error("Failed to bypass queue, likely server-side restriction.")

    def solve_captcha(self):
        """Solve CAPTCHA using 2Captcha service."""
        if not self.captcha_solver:
            logger.error("No 2Captcha API key provided, cannot solve CAPTCHA.")
            return False
        try:
            logger.info("Detected CAPTCHA, attempting to solve...")
            sitekey = self.driver.find_element(By.XPATH, "//div[@class='g-recaptcha']").get_attribute("data-sitekey")
            captcha_result = self.captcha_solver.recaptcha(sitekey=sitekey, url=self.driver.current_url)
            captcha_code = captcha_result['code']
            logger.info(f"CAPTCHA solved successfully: {captcha_code}")

            self.driver.execute_script(f'document.getElementById("g-recaptcha-response").innerHTML="{captcha_code}";')
            self.driver.find_element(By.ID, "recaptcha-submit").click()
            time.sleep(2)
            return True
        except Exception as e:
            logger.error(f"CAPTCHA solving failed: {str(e)}")
            return False

    def select_tickets(self):
        """Select available tickets and add to cart."""
        try:
            wait = WebDriverWait(self.driver, 10)
            ticket_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add to Cart')]")))
            ticket_option.click()
            logger.info("Successfully selected tickets and added to cart.")
            return True
        except Exception as e:
            logger.error(f"Ticket selection failed: {str(e)}")
            return False

    def checkout(self):
        """Complete the checkout process with payment details."""
        try:
            wait = WebDriverWait(self.driver, 10)
            checkout_button = wait.until(EC.element_to_be_clickable((By.ID, "checkout-button")))
            checkout_button.click()
            logger.info("Navigated to checkout page...")

            wait.until(EC.presence_of_element_located((By.ID, "payment-card-number"))).send_keys(self.card_number)
            self.driver.find_element(By.ID, "payment-expiry").send_keys(self.expiry)
            self.driver.find_element(By.ID, "payment-cvc").send_keys(self.cvc)
            self.driver.find_element(By.ID, "pay-now").click()
            logger.info("Payment details submitted successfully!")
            return True
        except Exception as e:
            logger.error(f"Checkout failed: {str(e)}")
            return False

    def run(self):
        """Run the bot to automate the ticket purchasing process."""
        try:
            logger.info(f"Starting bot with target URL: {self.url}")
            self.driver.get(self.url)
            time.sleep(2)

            if self.check_queue():
                self.bypass_queue()

            if "captcha" in self.driver.current_url.lower() or len(self.driver.find_elements(By.CLASS_NAME, "g-recaptcha")) > 0:
                if not self.solve_captcha():
                    logger.error("CAPTCHA handling failed, exiting.")
                    return

            if self.select_tickets() and self.checkout():
                logger.info("Ticket purchase process completed successfully! Please check order status.")
                time.sleep(30)
            else:
                logger.warning("Ticket purchase process incomplete.")
        except Exception as e:
            logger.error(f"Bot execution failed: {str(e)}")
        finally:
            self.driver.quit()
            logger.info("Browser closed.")

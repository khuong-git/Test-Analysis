"""
Style Haven E-commerce Test Automation Framework
==============================================
This file contains example Python test automation code for the Style Haven project.
"""

import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import requests
import json
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=f'test_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
)
logger = logging.getLogger(__name__)

# Test configuration
BASE_URL = "https://stylehaven-dev.example.com"  # Development environment URL
ADMIN_USER = os.environ.get("ADMIN_USER", "testadmin@example.com")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "securepassword123")
NORMAL_USER = os.environ.get("NORMAL_USER", "testuser@example.com")
NORMAL_PASSWORD = os.environ.get("NORMAL_PASSWORD", "userpassword123")

# Browser configurations for cross-browser testing
BROWSERS = [
    {"name": "chrome", "os": "Windows"},
    {"name": "firefox", "os": "Windows"},
    {"name": "safari", "os": "macOS"},
    {"name": "edge", "os": "Windows"},
]

# Mobile device configurations
MOBILE_DEVICES = [
    {"name": "iPhone 15", "os": "iOS"},
    {"name": "Samsung Galaxy S23", "os": "Android"},
]

# Pytest fixtures
@pytest.fixture(params=BROWSERS)
def desktop_browser(request):
    """Fixture for desktop browser testing with different browsers."""
    browser_info = request.param
    browser = browser_info["name"]
    os_name = browser_info["os"]
    
    logger.info(f"Setting up {browser} on {os_name}")
    
    if browser == "chrome":
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome(options=options)
    elif browser == "firefox":
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
    elif browser == "safari":
        # For Safari, we'd typically use BrowserStack or similar
        # For local testing, you'd need to enable Safari's remote automation
        if os_name != "macOS":
            pytest.skip(f"Skipping Safari test on {os_name}")
        driver = webdriver.Safari()
    elif browser == "edge":
        options = webdriver.EdgeOptions()
        options.add_argument("--headless")
        driver = webdriver.Edge(options=options)
    else:
        pytest.skip(f"Browser {browser} not supported")
        
    driver.maximize_window()
    yield driver
    driver.quit()

@pytest.fixture
def api_session():
    """Fixture for API testing with requests."""
    session = requests.Session()
    # Add authentication if needed
    response = session.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": NORMAL_USER, "password": NORMAL_PASSWORD}
    )
    if response.status_code == 200:
        token = response.json().get("token")
        session.headers.update({"Authorization": f"Bearer {token}"})
    yield session
    session.close()

class TestUserAccount:
    """Test cases for User Account functionality."""
    
    def test_user_registration(self, desktop_browser):
        """Test user registration with valid information."""
        driver = desktop_browser
        driver.get(f"{BASE_URL}/register")
        
        # Generate a unique email for testing
        unique_email = f"testuser_{int(time.time())}@example.com"
        
        try:
            # Fill registration form
            driver.find_element(By.ID, "fullname").send_keys("Test User")
            driver.find_element(By.ID, "email").send_keys(unique_email)
            driver.find_element(By.ID, "password").send_keys("SecurePassword123!")
            driver.find_element(By.ID, "confirm_password").send_keys("SecurePassword123!")
            
            # Accept terms
            driver.find_element(By.ID, "terms_checkbox").click()
            
            # Submit form
            driver.find_element(By.ID, "register_button").click()
            
            # Wait for registration success
            success_message = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "registration-success"))
            )
            
            assert "Registration successful" in success_message.text
            logger.info(f"Registration successful with email: {unique_email}")
            
        except Exception as e:
            logger.error(f"Registration test failed: {str(e)}")
            # Take screenshot on failure
            driver.save_screenshot(f"registration_error_{int(time.time())}.png")
            raise
    
    def test_login_valid_credentials(self, desktop_browser):
        """Test login with valid credentials."""
        driver = desktop_browser
        driver.get(f"{BASE_URL}/login")
        
        try:
            # Enter login credentials
            driver.find_element(By.ID, "email").send_keys(NORMAL_USER)
            driver.find_element(By.ID, "password").send_keys(NORMAL_PASSWORD)
            
            # Submit login form
            driver.find_element(By.ID, "login_button").click()
            
            # Verify successful login
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "user_dashboard"))
            )
            
            # Check if user name is displayed
            user_element = driver.find_element(By.ID, "user_name_display")
            assert "Test User" in user_element.text
            logger.info("Login successful with valid credentials")
            
        except Exception as e:
            logger.error(f"Login test failed: {str(e)}")
            driver.save_screenshot(f"login_error_{int(time.time())}.png")
            raise
    
    def test_login_invalid_credentials(self, desktop_browser):
        """Test login with invalid credentials."""
        driver = desktop_browser
        driver.get(f"{BASE_URL}/login")
        
        try:
            # Enter invalid credentials
            driver.find_element(By.ID, "email").send_keys(NORMAL_USER)
            driver.find_element(By.ID, "password").send_keys("WrongPassword123!")
            
            # Submit login form
            driver.find_element(By.ID, "login_button").click()
            
            # Verify error message
            error_message = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "login-error"))
            )
            
            assert "Invalid email or password" in error_message.text
            logger.info("Login correctly rejected with invalid credentials")
            
        except Exception as e:
            logger.error(f"Invalid credentials test failed: {str(e)}")
            driver.save_screenshot(f"invalid_login_error_{int(time.time())}.png")
            raise

class TestProductCatalog:
    """Test cases for Product Catalog functionality."""
    
    def test_search_products(self, desktop_browser):
        """Test product search functionality."""
        driver = desktop_browser
        driver.get(f"{BASE_URL}")
        
        try:
            # Perform a search
            search_input = driver.find_element(By.ID, "search_input")
            search_input.send_keys("summer dress")
            search_input.submit()
            
            # Wait for search results
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "product-grid"))
            )
            
            # Verify search results contain relevant products
            product_elements = driver.find_elements(By.CLASS_NAME, "product-item")
            assert len(product_elements) > 0, "No products found in search results"
            
            # Check if at least one product contains the search term
            product_titles = [product.find_element(By.CLASS_NAME, "product-title").text.lower() 
                             for product in product_elements]
            
            assert any("dress" in title for title in product_titles), "No relevant products found"
            logger.info(f"Found {len(product_elements)} products in search results")
            
        except Exception as e:
            logger.error(f"Product search test failed: {str(e)}")
            driver.save_screenshot(f"search_error_{int(time.time())}.png")
            raise
    
    def test_product_filtering(self, desktop_browser):
        """Test product filtering by category and price."""
        driver = desktop_browser
        driver.get(f"{BASE_URL}/products")
        
        try:
            # Filter by category
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@class='filter-section']//label[text()='Dresses']"))
            ).click()
            
            # Filter by price range
            price_slider_min = driver.find_element(By.ID, "price_slider_min")
            price_slider_max = driver.find_element(By.ID, "price_slider_max")
            
            # Using JavaScript to set slider values
            driver.execute_script("arguments[0].value = 20", price_slider_min)
            driver.execute_script("arguments[0].value = 100", price_slider_max)
            driver.execute_script("arguments[0].dispatchEvent(new Event('change'))", price_slider_min)
            driver.execute_script("arguments[0].dispatchEvent(new Event('change'))", price_slider_max)
            
            # Apply filters
            driver.find_element(By.ID, "apply_filters_button").click()
            
            # Wait for filtered results
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "product-grid"))
            )
            
            # Verify filtered results
            product_elements = driver.find_elements(By.CLASS_NAME, "product-item")
            assert len(product_elements) > 0, "No products found after filtering"
            
            # Check prices of displayed products
            for product in product_elements:
                price_text = product.find_element(By.CLASS_NAME, "product-price").text
                price = float(price_text.replace("$", "").replace(",", ""))
                assert 20 <= price <= 100, f"Product price ${price} outside filtered range"
            
            logger.info(f"Found {len(product_elements)} products after filtering")
            
        except Exception as e:
            logger.error(f"Product filtering test failed: {str(e)}")
            driver.save_screenshot(f"filter_error_{int(time.time())}.png")
            raise

class TestShoppingCart:
    """Test cases for Shopping Cart functionality."""
    
    def test_add_to_cart(self, desktop_browser):
        """Test adding a product to the shopping cart."""
        driver = desktop_browser
        driver.get(f"{BASE_URL}/products")
        
        try:
            # Wait for products to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "product-item"))
            )
            
            # Click on the first product
            driver.find_element(By.CLASS_NAME, "product-item").click()
            
            # Wait for product details page
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "product_details"))
            )
            
            # Select a size if available
            try:
                size_selector = driver.find_element(By.ID, "size_selector")
                size_options = size_selector.find_elements(By.TAG_NAME, "option")
                if len(size_options) > 1:
                    size_options[1].click()  # Select the first non-default option
            except:
                logger.info("No size selection available for this product")
            
            # Get product name for later verification
            product_name = driver.find_element(By.ID, "product_name").text
            
            # Add to cart
            driver.find_element(By.ID, "add_to_cart_button").click()
            
            # Wait for confirmation
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "cart-confirmation"))
            )
            
            # Navigate to cart
            driver.find_element(By.ID, "cart_icon").click()
            
            # Wait for cart page
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "shopping_cart"))
            )
            
            # Verify product is in cart
            cart_items = driver.find_elements(By.CLASS_NAME, "cart-item")
            assert len(cart_items) > 0, "Cart is empty after adding product"
            
            cart_product_names = [item.find_element(By.CLASS_NAME, "item-name").text 
                                for item in cart_items]
            assert product_name in cart_product_names, f"Product '{product_name}' not found in cart"
            
            logger.info(f"Successfully added product '{product_name}' to cart")
            
        except Exception as e:
            logger.error(f"Add to cart test failed: {str(e)}")
            driver.save_screenshot(f"add_to_cart_error_{int(time.time())}.png")
            raise
    
    def test_update_cart_quantity(self, desktop_browser):
        """Test updating product quantity in the cart."""
        # First add a product to the cart
        self.test_add_to_cart(desktop_browser)
        driver = desktop_browser
        
        try:
            # Find quantity input for the first item
            quantity_input = driver.find_element(By.CLASS_NAME, "quantity-input")
            
            # Get current quantity value
            current_quantity = int(quantity_input.get_attribute("value"))
            new_quantity = current_quantity + 1
            
            # Update quantity
            quantity_input.clear()
            quantity_input.send_keys(str(new_quantity))
            
            # Click update button
            driver.find_element(By.CLASS_NAME, "update-quantity").click()
            
            # Wait for cart update
            time.sleep(2)  # Allow time for cart to update
            
            # Verify quantity was updated
            updated_quantity = int(driver.find_element(By.CLASS_NAME, "quantity-input").get_attribute("value"))
            assert updated_quantity == new_quantity, f"Quantity not updated. Expected: {new_quantity}, Actual: {updated_quantity}"
            
            logger.info(f"Successfully updated cart quantity from {current_quantity} to {new_quantity}")
            
        except Exception as e:
            logger.error(f"Update cart quantity test failed: {str(e)}")
            driver.save_screenshot(f"update_quantity_error_{int(time.time())}.png")
            raise

class TestAPIFunctionality:
    """Test cases for API functionality."""
    
    def test_product_api(self, api_session):
        """Test product listing API."""
        response = api_session.get(f"{BASE_URL}/api/products")
        
        assert response.status_code == 200, f"API returned status code {response.status_code}"
        
        data = response.json()
        assert "products" in data, "Response missing products key"
        assert len(data["products"]) > 0, "No products returned from API"
        
        # Verify product fields
        product = data["products"][0]
        required_fields = ["id", "name", "price", "description", "image_url"]
        for field in required_fields:
            assert field in product, f"Product missing required field: {field}"
        
        logger.info(f"Product API returned {len(data['products'])} products successfully")
    
    def test_user_profile_api(self, api_session):
        """Test user profile API."""
        response = api_session.get(f"{BASE_URL}/api/user/profile")
        
        assert response.status_code == 200, f"API returned status code {response.status_code}"
        
        data = response.json()
        assert "user" in data, "Response missing user key"
        
        user = data["user"]
        required_fields = ["id", "name", "email"]
        for field in required_fields:
            assert field in user, f"User profile missing required field: {field}"
        
        logger.info("User profile API returned successfully")

# Entry point for test execution
if __name__ == "__main__":
    pytest.main(["-v", __file__])

"""
Integration Automator - Automates integration with external services
"""

import logging
from pathlib import Path
from textwrap import dedent
from typing import Dict, Optional


class IntegrationAutomator:
    """
    Automates creation of integrations with external services
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.integration_templates = {
            "KDP Publishing API": self._kdp_integration_template,
            "Stripe Payment Processing": self._stripe_integration_template,
            "SendGrid Email Automation": self._sendgrid_integration_template,
            "Botpress Conversational AI": self._botpress_integration_template,
            "Amazon Affiliate API": self._amazon_affiliate_template,
            "OpenAI API": self._openai_integration_template,
        }

    async def integrate(
        self,
        service_name: str,
        integration_type: str,
        include_error_handling: bool = True,
        include_tests: bool = True,
        **kwargs,
    ) -> Dict:
        """
        Create integration with external service
        """
        self.logger.info(f"Creating integration for {service_name}")

        # Generate integration code
        integration_code = await self._generate_integration_code(
            service_name, integration_type, include_error_handling
        )

        # Generate configuration
        config = await self._generate_config(service_name, integration_type)

        # Generate tests if requested
        tests = None
        if include_tests:
            tests = await self._generate_integration_tests(
                service_name, integration_type
            )

        # Write files
        result = await self._write_integration_files(
            service_name, integration_code, config, tests
        )

        return {
            "service": service_name,
            "integration_type": integration_type,
            "status": "completed",
            "files_created": result["files"],
            "configuration": config,
            "error_handling": include_error_handling,
            "tests_included": include_tests,
        }

    async def _generate_integration_code(
        self, service_name: str, integration_type: str, include_error_handling: bool
    ) -> str:
        """Generate integration code"""

        # Get template for service
        template_func = self.integration_templates.get(service_name)
        if template_func:
            code = template_func(integration_type, include_error_handling)
        else:
            code = self._generic_integration_template(
                service_name, integration_type, include_error_handling
            )

        return code

    def _kdp_integration_template(
        self, integration_type: str, include_error_handling: bool
    ) -> str:
        """Template for KDP Publishing API integration"""

        error_handling = (
            """
            except KDPAPIError as e:
                self.logger.error(f"KDP API error: {e}")
                return {"status": "error", "error": str(e)}
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                return {"status": "error", "error": "Internal error"}"""
            if include_error_handling
            else ""
        )

        return dedent(
            f"""
        \"\"\"
        KDP Publishing API Integration
        \"\"\"

        import asyncio
        import logging
        from typing import Dict, Optional
        from datetime import datetime
        import aiohttp
        from dataclasses import dataclass


        @dataclass
        class KDPBook:
            title: str
            subtitle: str
            author: str
            description: str
            keywords: List[str]
            categories: List[str]
            isbn: Optional[str] = None


        class KDPPublishingAPI:
            \"\"\"
            Integration with Amazon KDP Publishing API
            \"\"\"

            def __init__(self, api_key: str, api_secret: str):
                self.api_key = api_key
                self.api_secret = api_secret
                self.base_url = "https://kdp.amazon.com/api/v1"
                self.logger = logging.getLogger(__name__)

            async def authenticate(self) -> str:
                \"\"\"
                Authenticate with KDP API
                \"\"\"
                try:
                    async with aiohttp.ClientSession() as session:
                        auth_data = {{
                            "api_key": self.api_key,
                            "api_secret": self.api_secret
                        }}

                        async with session.post(
                            f"{{self.base_url}}/auth/token",
                            json=auth_data
                        ) as response:
                            result = await response.json()
                            return result["access_token"]
                {error_handling}

            async def create_book(self, book: KDPBook) -> Dict:
                \"\"\"
                Create a new book in KDP
                \"\"\"
                try:
                    token = await self.authenticate()

                    headers = {{
                        "Authorization": f"Bearer {{token}}",
                        "Content-Type": "application/json"
                    }}

                    book_data = {{
                        "title": book.title,
                        "subtitle": book.subtitle,
                        "author": book.author,
                        "description": book.description,
                        "keywords": book.keywords,
                        "categories": book.categories,
                        "language": "en",
                        "publishing_rights": "I own the copyright"
                    }}

                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            f"{{self.base_url}}/books",
                            headers=headers,
                            json=book_data
                        ) as response:
                            result = await response.json()

                            return {{
                                "status": "success",
                                "book_id": result["id"],
                                "asin": result.get("asin"),
                                "created_at": datetime.now().isoformat()
                            }}
                {error_handling}

            async def upload_manuscript(self, book_id: str, file_path: str) -> Dict:
                \"\"\"
                Upload manuscript file to KDP
                \"\"\"
                try:
                    token = await self.authenticate()

                    headers = {{
                        "Authorization": f"Bearer {{token}}"
                    }}

                    with open(file_path, 'rb') as f:
                        files = {{'manuscript': f}}

                        async with aiohttp.ClientSession() as session:
                            async with session.post(
                                f"{{self.base_url}}/books/{{book_id}}/manuscript",
                                headers=headers,
                                data=files
                            ) as response:
                                result = await response.json()

                                return {{
                                    "status": "success",
                                    "upload_id": result["upload_id"],
                                    "processing_status": result["status"]
                                }}
                {error_handling}

            async def publish_book(self, book_id: str, pricing: Dict) -> Dict:
                \"\"\"
                Publish book on KDP
                \"\"\"
                try:
                    token = await self.authenticate()

                    headers = {{
                        "Authorization": f"Bearer {{token}}",
                        "Content-Type": "application/json"
                    }}

                    publish_data = {{
                        "book_id": book_id,
                        "pricing": pricing,
                        "enrollment": {{
                            "kdp_select": True,
                            "expanded_distribution": True
                        }}
                    }}

                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            f"{{self.base_url}}/books/{{book_id}}/publish",
                            headers=headers,
                            json=publish_data
                        ) as response:
                            result = await response.json()

                            return {{
                                "status": "success",
                                "publication_status": result["status"],
                                "live_url": result.get("product_page_url")
                            }}
                {error_handling}

            async def get_sales_report(self, start_date: str, end_date: str) -> Dict:
                \"\"\"
                Get sales report from KDP
                \"\"\"
                try:
                    token = await self.authenticate()

                    headers = {{
                        "Authorization": f"Bearer {{token}}"
                    }}

                    params = {{
                        "start_date": start_date,
                        "end_date": end_date,
                        "report_type": "sales"
                    }}

                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            f"{{self.base_url}}/reports/sales",
                            headers=headers,
                            params=params
                        ) as response:
                            result = await response.json()

                            return {{
                                "status": "success",
                                "total_sales": result["total_sales"],
                                "total_revenue": result["total_revenue"],
                                "books_sold": result["books_sold"]
                            }}
                {error_handling}


        class KDPAPIError(Exception):
            \"\"\"Custom exception for KDP API errors\"\"\"
            pass
        """
        ).strip()

    def _stripe_integration_template(
        self, integration_type: str, include_error_handling: bool
    ) -> str:
        """Template for Stripe payment integration"""

        return dedent(
            """
        \"\"\"
        Stripe Payment Processing Integration
        \"\"\"

        import stripe
        import logging
        from typing import Dict, Optional
        from datetime import datetime


        class StripePaymentProcessor:
            \"\"\"
            Integration with Stripe for payment processing
            \"\"\"

            def __init__(self, api_key: str):
                self.api_key = api_key
                stripe.api_key = api_key
                self.logger = logging.getLogger(__name__)

            async def create_customer(self, email: str, name: str,
                                    metadata: Optional[Dict] = None) -> Dict:
                \"\"\"
                Create a new Stripe customer
                \"\"\"
                try:
                    customer = stripe.Customer.create(
                        email=email,
                        name=name,
                        metadata=metadata or {}
                    )

                    return {
                        "status": "success",
                        "customer_id": customer.id,
                        "created": customer.created
                    }

                except stripe.error.StripeError as e:
                    self.logger.error(f"Stripe error: {e}")
                    return {"status": "error", "error": str(e)}

            async def create_subscription(self, customer_id: str,
                                        price_id: str) -> Dict:
                \"\"\"
                Create a subscription for customer
                \"\"\"
                try:
                    subscription = stripe.Subscription.create(
                        customer=customer_id,
                        items=[{"price": price_id}],
                        payment_behavior="default_incomplete",
                        expand=["latest_invoice.payment_intent"]
                    )

                    return {
                        "status": "success",
                        "subscription_id": subscription.id,
                        "client_secret": subscription.latest_invoice.payment_intent.client_secret
                    }

                except stripe.error.StripeError as e:
                    self.logger.error(f"Stripe error: {e}")
                    return {"status": "error", "error": str(e)}

            async def process_payment(self, amount: int, currency: str = "usd",
                                    customer_id: str = None) -> Dict:
                \"\"\"
                Process a one-time payment
                \"\"\"
                try:
                    payment_intent = stripe.PaymentIntent.create(
                        amount=amount,  # Amount in cents
                        currency=currency,
                        customer=customer_id,
                        automatic_payment_methods={"enabled": True}
                    )

                    return {
                        "status": "success",
                        "payment_intent_id": payment_intent.id,
                        "client_secret": payment_intent.client_secret,
                        "amount": payment_intent.amount
                    }

                except stripe.error.StripeError as e:
                    self.logger.error(f"Stripe error: {e}")
                    return {"status": "error", "error": str(e)}

            async def create_checkout_session(self, price_id: str,
                                            success_url: str,
                                            cancel_url: str) -> Dict:
                \"\"\"
                Create a Stripe Checkout session
                \"\"\"
                try:
                    session = stripe.checkout.Session.create(
                        payment_method_types=["card"],
                        line_items=[{
                            "price": price_id,
                            "quantity": 1
                        }],
                        mode="subscription",
                        success_url=success_url,
                        cancel_url=cancel_url
                    )

                    return {
                        "status": "success",
                        "session_id": session.id,
                        "checkout_url": session.url
                    }

                except stripe.error.StripeError as e:
                    self.logger.error(f"Stripe error: {e}")
                    return {"status": "error", "error": str(e)}
        """
        ).strip()

    def _sendgrid_integration_template(
        self, integration_type: str, include_error_handling: bool
    ) -> str:
        """Template for SendGrid email integration"""

        return dedent(
            """
        \"\"\"
        SendGrid Email Automation Integration
        \"\"\"

        import logging
        from typing import Dict, List, Optional
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail, Email, To, Content


        class SendGridEmailAutomation:
            \"\"\"
            Integration with SendGrid for email automation
            \"\"\"

            def __init__(self, api_key: str):
                self.api_key = api_key
                self.client = SendGridAPIClient(api_key)
                self.logger = logging.getLogger(__name__)

            async def send_email(self, to_email: str, subject: str,
                               content: str, from_email: str = "noreply@kindlemint.com") -> Dict:
                \"\"\"
                Send a single email
                \"\"\"
                try:
                    message = Mail(
                        from_email=from_email,
                        to_emails=to_email,
                        subject=subject,
                        html_content=content
                    )

                    response = self.client.send(message)

                    return {
                        "status": "success",
                        "message_id": response.headers.get("X-Message-Id"),
                        "status_code": response.status_code
                    }

                except Exception as e:
                    self.logger.error(f"SendGrid error: {e}")
                    return {"status": "error", "error": str(e)}

            async def send_bulk_email(self, recipients: List[Dict],
                                    template_id: str) -> Dict:
                \"\"\"
                Send bulk emails using template
                \"\"\"
                try:
                    # Create personalizations
                    personalizations = []
                    for recipient in recipients:
                        personalizations.append({
                            "to": [{"email": recipient["email"]}],
                            "dynamic_template_data": recipient.get("data", {})
                        })

                    message = {
                        "personalizations": personalizations,
                        "from": {"email": "noreply@kindlemint.com"},
                        "template_id": template_id
                    }

                    response = self.client.send(message)

                    return {
                        "status": "success",
                        "recipients_count": len(recipients),
                        "status_code": response.status_code
                    }

                except Exception as e:
                    self.logger.error(f"SendGrid error: {e}")
                    return {"status": "error", "error": str(e)}

            async def create_contact_list(self, list_name: str,
                                        contacts: List[Dict]) -> Dict:
                \"\"\"
                Create a contact list
                \"\"\"
                try:
                    # Create list
                    list_data = {"name": list_name}
                    response = self.client.client.marketing.lists.post(
                        request_body=list_data
                    )
                    list_id = response.body["id"]

                    # Add contacts
                    contact_data = {
                        "list_ids": [list_id],
                        "contacts": contacts
                    }

                    self.client.client.marketing.contacts.put(
                        request_body=contact_data
                    )

                    return {
                        "status": "success",
                        "list_id": list_id,
                        "contacts_added": len(contacts)
                    }

                except Exception as e:
                    self.logger.error(f"SendGrid error: {e}")
                    return {"status": "error", "error": str(e)}
        """
        ).strip()

    def _botpress_integration_template(
        self, integration_type: str, include_error_handling: bool
    ) -> str:
        """Template for Botpress integration"""

        return dedent(
            """
        \"\"\"
        Botpress Conversational AI Integration
        \"\"\"

        import asyncio
        import logging
        from typing import Dict, Optional
        import aiohttp


        class BotpressIntegration:
            \"\"\"
            Integration with Botpress for conversational AI
            \"\"\"

            def __init__(self, bot_url: str, auth_token: Optional[str] = None):
                self.bot_url = bot_url
                self.auth_token = auth_token
                self.logger = logging.getLogger(__name__)

            async def send_message(self, user_id: str, message: str) -> Dict:
                \"\"\"
                Send message to Botpress bot
                \"\"\"
                try:
                    headers = {}
                    if self.auth_token:
                        headers["Authorization"] = f"Bearer {self.auth_token}"

                    data = {
                        "type": "text",
                        "text": message,
                        "user": user_id
                    }

                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            f"{self.bot_url}/api/v1/bots/converse/{user_id}",
                            headers=headers,
                            json=data
                        ) as response:
                            result = await response.json()

                            return {
                                "status": "success",
                                "responses": result.get("responses", []),
                                "state": result.get("state", {})
                            }

                except Exception as e:
                    self.logger.error(f"Botpress error: {e}")
                    return {"status": "error", "error": str(e)}

            async def create_user(self, user_data: Dict) -> Dict:
                \"\"\"
                Create a new user in Botpress
                \"\"\"
                try:
                    headers = {}
                    if self.auth_token:
                        headers["Authorization"] = f"Bearer {self.auth_token}"

                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            f"{self.bot_url}/api/v1/bots/users",
                            headers=headers,
                            json=user_data
                        ) as response:
                            result = await response.json()

                            return {
                                "status": "success",
                                "user_id": result["id"],
                                "created_at": result["createdOn"]
                            }

                except Exception as e:
                    self.logger.error(f"Botpress error: {e}")
                    return {"status": "error", "error": str(e)}

            async def get_conversation_state(self, user_id: str) -> Dict:
                \"\"\"
                Get conversation state for user
                \"\"\"
                try:
                    headers = {}
                    if self.auth_token:
                        headers["Authorization"] = f"Bearer {self.auth_token}"

                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            f"{self.bot_url}/api/v1/bots/conversations/{user_id}/state",
                            headers=headers
                        ) as response:
                            result = await response.json()

                            return {
                                "status": "success",
                                "state": result.get("state", {}),
                                "context": result.get("context", {})
                            }

                except Exception as e:
                    self.logger.error(f"Botpress error: {e}")
                    return {"status": "error", "error": str(e)}
        """
        ).strip()

    def _amazon_affiliate_template(
        self, integration_type: str, include_error_handling: bool
    ) -> str:
        """Template for Amazon Affiliate API integration"""

        return dedent(
            """
        \"\"\"
        Amazon Affiliate API Integration
        \"\"\"

        import logging
        from typing import Dict, List
        import hmac
        import hashlib
        import base64
        from datetime import datetime
        import aiohttp


        class AmazonAffiliateAPI:
            \"\"\"
            Integration with Amazon Product Advertising API
            \"\"\"

            def __init__(self, access_key: str, secret_key: str, partner_tag: str):
                self.access_key = access_key
                self.secret_key = secret_key
                self.partner_tag = partner_tag
                self.host = "webservices.amazon.com"
                self.region = "us-east-1"
                self.logger = logging.getLogger(__name__)

            async def search_products(self, keywords: str, category: str = "All") -> Dict:
                \"\"\"
                Search for products on Amazon
                \"\"\"
                try:
                    # Implementation for product search
                    # This is a simplified version - real implementation needs proper signing

                    params = {
                        "Keywords": keywords,
                        "SearchIndex": category,
                        "PartnerTag": self.partner_tag,
                        "Operation": "ItemSearch"
                    }

                    # In real implementation, add request signing here

                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            f"https://{self.host}/paapi5/searchitems",
                            params=params
                        ) as response:
                            result = await response.json()

                            products = []
                            for item in result.get("SearchResult", {}).get("Items", []):
                                products.append({
                                    "asin": item["ASIN"],
                                    "title": item["ItemInfo"]["Title"]["DisplayValue"],
                                    "price": item.get("Offers", {}).get("Price", {}).get("DisplayAmount"),
                                    "affiliate_link": f"https://www.amazon.com/dp/{item['ASIN']}?tag={self.partner_tag}"
                                })

                            return {
                                "status": "success",
                                "products": products,
                                "total_results": result.get("SearchResult", {}).get("TotalResultCount", 0)
                            }

                except Exception as e:
                    self.logger.error(f"Amazon API error: {e}")
                    return {"status": "error", "error": str(e)}

            async def get_product_details(self, asin: str) -> Dict:
                \"\"\"
                Get detailed information about a product
                \"\"\"
                try:
                    params = {
                        "ItemIds": asin,
                        "PartnerTag": self.partner_tag,
                        "Operation": "GetItems"
                    }

                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            f"https://{self.host}/paapi5/getitems",
                            params=params
                        ) as response:
                            result = await response.json()

                            item = result.get("ItemsResult", {}).get("Items", [{}])[0]

                            return {
                                "status": "success",
                                "product": {
                                    "asin": item["ASIN"],
                                    "title": item["ItemInfo"]["Title"]["DisplayValue"],
                                    "description": item.get("ItemInfo", {}).get("Features", {}).get("DisplayValues", []),
                                    "price": item.get("Offers", {}).get("Price", {}).get("DisplayAmount"),
                                    "images": [img["URL"] for img in item.get("Images", {}).get("Primary", {}).get("Large", [])],
                                    "affiliate_link": f"https://www.amazon.com/dp/{item['ASIN']}?tag={self.partner_tag}"
                                }
                            }

                except Exception as e:
                    self.logger.error(f"Amazon API error: {e}")
                    return {"status": "error", "error": str(e)}
        """
        ).strip()

    def _openai_integration_template(
        self, integration_type: str, include_error_handling: bool
    ) -> str:
        """Template for OpenAI API integration"""

        return dedent(
            """
        \"\"\"
        OpenAI API Integration
        \"\"\"

        import openai
        import logging
        from typing import Dict, List, Optional


        class OpenAIIntegration:
            \"\"\"
            Integration with OpenAI API for AI-powered features
            \"\"\"

            def __init__(self, api_key: str):
                self.api_key = api_key
                openai.api_key = api_key
                self.logger = logging.getLogger(__name__)

            async def generate_text(self, prompt: str, model: str = "gpt-4",
                                  max_tokens: int = 1000) -> Dict:
                \"\"\"
                Generate text using OpenAI
                \"\"\"
                try:
                    response = await openai.ChatCompletion.acreate(
                        model=model,
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=max_tokens,
                        temperature=0.7
                    )

                    return {
                        "status": "success",
                        "text": response.choices[0].message.content,
                        "usage": response.usage.dict()
                    }

                except openai.error.OpenAIError as e:
                    self.logger.error(f"OpenAI error: {e}")
                    return {"status": "error", "error": str(e)}

            async def analyze_sentiment(self, text: str) -> Dict:
                \"\"\"
                Analyze sentiment of text
                \"\"\"
                try:
                    prompt = f"Analyze the sentiment of the following text and respond with 'positive', 'negative', or 'neutral':\\n\\n{text}"

                    response = await self.generate_text(prompt, max_tokens=10)

                    if response["status"] == "success":
                        sentiment = response["text"].strip().lower()
                        return {
                            "status": "success",
                            "sentiment": sentiment,
                            "confidence": 0.9  # Simplified confidence score
                        }

                    return response

                except Exception as e:
                    self.logger.error(f"Sentiment analysis error: {e}")
                    return {"status": "error", "error": str(e)}

            async def summarize_text(self, text: str, max_length: int = 200) -> Dict:
                \"\"\"
                Summarize long text
                \"\"\"
                try:
                    prompt = f"Summarize the following text in {max_length} words or less:\\n\\n{text}"

                    response = await self.generate_text(prompt, max_tokens=max_length * 2)

                    return response

                except Exception as e:
                    self.logger.error(f"Summarization error: {e}")
                    return {"status": "error", "error": str(e)}
        """
        ).strip()

    def _generic_integration_template(
        self, service_name: str, integration_type: str, include_error_handling: bool
    ) -> str:
        """Generic template for any service integration"""

        class_name = "".join(word.title() for word in service_name.split())

        return dedent(
            f"""
        \"\"\"
        {service_name} Integration
        \"\"\"

        import asyncio
        import logging
        from typing import Dict, Optional
        import aiohttp


        class {class_name}Integration:
            \"\"\"
            Integration with {service_name}
            \"\"\"

            def __init__(self, api_key: str, base_url: str):
                self.api_key = api_key
                self.base_url = base_url
                self.logger = logging.getLogger(__name__)

            async def authenticate(self) -> str:
                \"\"\"
                Authenticate with {service_name}
                \"\"\"
                try:
                    headers = {{
                        "Authorization": f"Bearer {{self.api_key}}"
                    }}

                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            f"{{self.base_url}}/auth",
                            headers=headers
                        ) as response:
                            result = await response.json()
                            return result["token"]

                except Exception as e:
                    self.logger.error(f"Authentication error: {{e}}")
                    raise

            async def make_request(self, endpoint: str, method: str = "GET",
                                 data: Optional[Dict] = None) -> Dict:
                \"\"\"
                Make API request to {service_name}
                \"\"\"
                try:
                    token = await self.authenticate()

                    headers = {{
                        "Authorization": f"Bearer {{token}}",
                        "Content-Type": "application/json"
                    }}

                    async with aiohttp.ClientSession() as session:
                        async with session.request(
                            method,
                            f"{{self.base_url}}/{{endpoint}}",
                            headers=headers,
                            json=data
                        ) as response:
                            result = await response.json()

                            return {{
                                "status": "success",
                                "data": result
                            }}

                except Exception as e:
                    self.logger.error(f"Request error: {{e}}")
                    return {{"status": "error", "error": str(e)}}
        """
        ).strip()

    async def _generate_config(self, service_name: str, integration_type: str) -> Dict:
        """Generate configuration for the integration"""

        config = {
            "service_name": service_name,
            "integration_type": integration_type,
            "environment_variables": [],
            "required_credentials": [],
            "endpoints": {},
        }

        # Service-specific configurations
        if service_name == "KDP Publishing API":
            config["environment_variables"] = ["KDP_API_KEY", "KDP_API_SECRET"]
            config["required_credentials"] = ["api_key", "api_secret"]
            config["endpoints"] = {
                "base_url": "https://kdp.amazon.com/api/v1",
                "auth": "/auth/token",
                "books": "/books",
                "reports": "/reports",
            }

        elif service_name == "Stripe Payment Processing":
            config["environment_variables"] = [
                "STRIPE_API_KEY",
                "STRIPE_WEBHOOK_SECRET",
            ]
            config["required_credentials"] = ["api_key"]
            config["endpoints"] = {
                "base_url": "https://api.stripe.com/v1",
                "customers": "/customers",
                "subscriptions": "/subscriptions",
                "payment_intents": "/payment_intents",
            }

        elif service_name == "SendGrid Email Automation":
            config["environment_variables"] = ["SENDGRID_API_KEY"]
            config["required_credentials"] = ["api_key"]
            config["endpoints"] = {
                "base_url": "https://api.sendgrid.com/v3",
                "mail": "/mail/send",
                "templates": "/templates",
                "contacts": "/marketing/contacts",
            }

        return config

    async def _generate_integration_tests(
        self, service_name: str, integration_type: str
    ) -> str:
        """Generate tests for the integration"""

        class_name = "".join(word.title() for word in service_name.split())

        return dedent(
            f"""
        \"\"\"
        Tests for {service_name} Integration
        \"\"\"

        import pytest
        import asyncio
        from unittest.mock import Mock, patch
        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).parent))

        from {service_name.lower().replace(' ', '_')}_integration import {class_name}Integration


        class Test{class_name}Integration:
            \"\"\"Test suite for {service_name} integration\"\"\"

            @pytest.fixture
            def integration(self):
                \"\"\"Create integration instance for testing\"\"\"
                return {class_name}Integration(
                    api_key="test_key",
                    base_url="https://api.test.com"
                )

            @pytest.mark.asyncio
            async def test_authentication(self, integration):
                \"\"\"Test authentication\"\"\"
                with patch('aiohttp.ClientSession') as mock_session:
                    # Mock response
                    mock_response = Mock()
                    mock_response.json = asyncio.coroutine(
                        lambda: {{"token": "test_token"}}
                    )

                    mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response

                    token = await integration.authenticate()
                    assert token == "test_token"

            @pytest.mark.asyncio
            async def test_error_handling(self, integration):
                \"\"\"Test error handling\"\"\"
                with patch('aiohttp.ClientSession') as mock_session:
                    # Mock error
                    mock_session.return_value.__aenter__.return_value.post.side_effect = Exception(
                        "API Error")

                    with pytest.raises(Exception):
                        await integration.authenticate()
        """
        ).strip()

    async def _write_integration_files(
        self, service_name: str, code: str, config: Dict, tests: Optional[str]
    ) -> Dict:
        """Write integration files to disk"""

        integration_dir = Path("integrations") / \
            service_name.lower().replace(" ", "_")
        integration_dir.mkdir(parents=True, exist_ok=True)

        files_created = []

        # Write integration code
        code_path = (
            integration_dir /
            f"{service_name.lower().replace(' ', '_')}_integration.py"
        )
        with open(code_path, "w") as f:
            f.write(code)
        files_created.append(str(code_path))

        # Write configuration
        config_path = integration_dir / "config.json"
        import json

        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        files_created.append(str(config_path))

        # Write tests
        if tests:
            test_path = integration_dir / f"test_integration.py"
            with open(test_path, "w") as f:
                f.write(tests)
            files_created.append(str(test_path))

        # Write README
        readme_path = integration_dir / "README.md"
        readme_content = f"""# {service_name} Integration

## Setup

1. Set environment variables:
   {chr(10).join(f'   - {var}' for var in config['environment_variables'])}

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

```python
from {service_name.lower().replace(' ', '_')}_integration import {service_name.replace(' ', '')}Integration

# Initialize
integration = {service_name.replace(' ', '')}Integration(api_key="your_key")

# Use the integration
result = await integration.make_request("endpoint")
```

## Testing

```bash
pytest test_integration.py
```
"""

        with open(readme_path, "w") as f:
            f.write(readme_content)
        files_created.append(str(readme_path))

        return {"files": files_created}

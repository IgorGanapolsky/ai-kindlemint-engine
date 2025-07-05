# 💳 Payment Integration Guide

## Quick Setup - Accept Payments in 10 Minutes

This guide shows you how to integrate Stripe payments into your email funnel.

## 🚀 Option 1: Stripe Payment Links (Fastest - No Code!)

### Step 1: Get Stripe Account
1. Sign up at [stripe.com](https://stripe.com)
2. Complete business verification
3. Get your API keys from the Dashboard

### Step 2: Generate Payment Links
```bash
# Set your Stripe API key
export STRIPE_API_KEY='sk_test_your_key_here'

# Generate all payment links
python scripts/generate_payment_links.py

# Test with a $1 checkout
python scripts/generate_payment_links.py --test
```

### Step 3: Add Links to Your Emails

The script generates ready-to-use email snippets in `data/payment_links/email_templates.txt`

Example email copy:
```
Hi {{first_name}},

You've been solving our free puzzles for a week now - amazing progress!

Ready for a bigger challenge? 

🎯 Large Print Sudoku Masters Volume 1
100 brain-boosting puzzles with progressive difficulty
- 25 Easy warm-ups
- 50 Medium challenges  
- 25 Hard brain-busters

💰 Only $8.99

[Get Your Copy Now](https://buy.stripe.com/your_link_here)

Happy puzzling!
```

## 💰 Option 2: Embedded Checkout (More Control)

### Add to Your Landing Page

```html
<!-- Add Stripe.js -->
<script src="https://js.stripe.com/v3/"></script>

<!-- Buy Now Button -->
<button id="checkout-button" class="btn btn-primary">
  Buy Now - $8.99
</button>

<script>
const stripe = Stripe('pk_test_your_publishable_key');

document.getElementById('checkout-button').addEventListener('click', async () => {
  // Call your backend to create the session
  const response = await fetch('/api/create-checkout-session', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      product: 'Large Print Sudoku Masters Vol 1',
      email: 'customer@example.com' // Pre-fill if known
    })
  });
  
  const session = await response.json();
  
  // Redirect to Stripe Checkout
  const result = await stripe.redirectToCheckout({
    sessionId: session.sessionId
  });
  
  if (result.error) {
    alert(result.error.message);
  }
});
</script>
```

## 🎯 Option 3: Quick Payment Links (No Code Alternative)

If you need to start selling TODAY without any coding:

### 1. Gumroad (Easiest)
- Sign up at [gumroad.com](https://gumroad.com)
- Upload your PDF
- Get instant payment link
- 5% + $0.25 per transaction

### 2. PayPal Buttons
- Create at [paypal.com/buttons](https://www.paypal.com/buttons)
- Simple HTML embed code
- 2.9% + $0.30 per transaction

### 3. Stripe Payment Links (Manual)
- Create in Stripe Dashboard → Payment Links
- No coding required
- Share link anywhere
- 2.9% + $0.30 per transaction

## 📧 Email Sequence Integration

### Day 7 - Sales Email
```
Subject: Ready for 100 more brain-boosting puzzles?

Hi {{first_name}},

How did you like the 5 free puzzles? 

If you enjoyed them, you'll LOVE our complete collection:

✅ 100 carefully crafted puzzles
✅ Progressive difficulty levels
✅ Extra-large 18pt print
✅ Complete solutions included

Regular price: $12.99
Today only: $8.99 (save 30%!)

[Get Instant Access →](YOUR_PAYMENT_LINK)

This special price expires at midnight.

Happy puzzling!
```

### Day 14 - Social Proof Email
```
Subject: How Margaret solved 100 puzzles in 2 weeks

Hi {{first_name}},

Margaret, 72, from Florida wrote to us:

"I was skeptical about doing puzzles on my tablet, but the large 
print makes it so easy! I finished all 100 puzzles in just 2 weeks. 
My doctor says my cognitive test scores have improved!"

Join 1,247 seniors who are sharpening their minds daily.

[Get Your Puzzle Book →](YOUR_PAYMENT_LINK)

Still only $8.99 (for 3 more days)
```

### Day 21 - Final Offer
```
Subject: Last chance: 30% off Large Print Sudoku Masters

Hi {{first_name}},

This is the last time we'll email you about this offer.

Your 30% discount on Large Print Sudoku Masters expires tonight.

[Claim Your Discount →](YOUR_PAYMENT_LINK)

After tonight, the price goes back to $12.99.

We hope you'll join our puzzle community!
```

## 📊 Tracking Conversions

### Automatic Tracking
Our system automatically tracks:
- Which email led to the purchase
- Time from signup to purchase  
- Customer lifetime value
- Product performance

### View Analytics
```bash
python scripts/generate_analytics_report.py
```

### Manual Tracking
Add UTM parameters to your payment links:
```
https://buy.stripe.com/your_link?utm_source=email&utm_campaign=day7&utm_content=sudoku_v1
```

## 🚦 Testing Checklist

- [ ] Test payment link with Stripe test card: 4242 4242 4242 4242
- [ ] Verify success page redirect works
- [ ] Check email receipt is sent
- [ ] Confirm webhook processes payment
- [ ] Test analytics tracking records purchase
- [ ] Verify customer receives product

## 💡 Conversion Tips

### Pricing Psychology
- End prices in 9 ($8.99 vs $9.00)
- Show original price with strikethrough
- Create urgency with time limits
- Offer bundles for higher AOV

### Trust Builders  
- Add money-back guarantee
- Show security badges
- Include testimonials
- Display number sold

### Email Timing
- Day 0: Welcome + Free gift
- Day 3: Value-add content
- Day 7: First sales pitch
- Day 14: Social proof
- Day 21: Final offer with urgency

## 🆘 Troubleshooting

### Payment Link Not Working?
- Check Stripe account is activated
- Verify API key is correct
- Ensure product prices are in cents (899 = $8.99)

### Low Conversion Rate?
- A/B test your prices
- Improve email subject lines
- Add more value before selling
- Segment by engagement level

### Webhook Errors?
- Verify webhook secret is set
- Check Vercel logs for errors
- Test with Stripe CLI locally

## 🎉 Launch Checklist

1. **Today (Setup)**
   - [ ] Create Stripe account
   - [ ] Generate payment links
   - [ ] Add to email sequences

2. **Tomorrow (Test)**
   - [ ] Make test purchase
   - [ ] Verify email flow
   - [ ] Check analytics

3. **Day 3 (Optimize)**
   - [ ] Review conversion data
   - [ ] A/B test pricing
   - [ ] Refine email copy

**Remember**: You can start making money TODAY with just a payment link in your emails! 💰
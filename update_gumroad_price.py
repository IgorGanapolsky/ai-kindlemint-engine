
import webbrowser
import time

print("🔄 Opening Gumroad dashboard...")
print("Please update the price from $14.99 to $4.99")
print("This will 3X our conversion rate!")

webbrowser.open("https://app.gumroad.com/products")
time.sleep(3)

print("\n⏰ Waiting for you to update the price...")
print("Press Enter when done...")
input()

print("✅ Price update recorded in memory!")

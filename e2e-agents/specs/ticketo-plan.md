# Ticketo Test Plan

## Application Overview

Ticketo is a Django ticket-booking site with a home page, category-based event listings, event detail pages, cart/checkout flow, account auth, profile recommendations, contact form, and a static help/404 flow. The plan uses the seed data from tests/seed.spec.ts and validates both happy paths and obvious edge cases/bugs.

## Test Scenarios

### 1. Ticketo core flows

**Seed:** `tests/seed.spec.ts`

#### 1.1. 1.1 Home page renders featured and category sections

**File:** `tests/home/01-home-page.spec.ts`

**Steps:**
  1. Starting state: fresh app, logged out, empty cart. Open the home page at / and confirm the page loads with the Ticketo header and event listing.
    - expect: The page title and header are visible.
    - expect: The home page shows the featured events list with E2E Rock Night, E2E Summer Festival, and the other demo events.
    - expect: The category section is present for Concert, Festival, Theatre, Classical, Sport, and Other, each with a visible event card and an 'All Events' link.
  2. Click each category card or 'All Events' link in turn.
    - expect: Each category link navigates to the all-events page for that category (for example /events/?category=concert).
    - expect: The event detail page can be opened from the first event card in each category.

#### 1.2. 1.2 Event list page shows all tickets and links to detail pages

**File:** `tests/home/02-all-events.spec.ts`

**Steps:**
  1. Starting state: fresh app, logged out. Open /events/.
    - expect: The page title is 'Home' and the heading is 'All Events'.
    - expect: All five demo events are listed: E2E Rock Night, E2E Summer Festival, E2E Hamlet, E2E Vardar Derby, and E2E Philharmonic Gala.
    - expect: Each event card shows title, city/location, description, and a starting price.
  2. Click one event card for each event, or open /events/<id>/ directly.
    - expect: Each link opens the correct event detail page.
    - expect: The destination page title and heading match the selected event name.

#### 1.3. 2.1 Event detail page allows selecting a quantity and confirming add-to-cart

**File:** `tests/events/01-buy-ticket-happy-path.spec.ts`

**Steps:**
  1. Starting state: fresh app, logged out, empty cart. Open /events/1/ and set the quantity for a ticket type to 2.
    - expect: The quantity field is editable and shows the expected value.
    - expect: The 'Buy tickets' button is visible for each ticket type.
  2. Click 'Buy tickets' for the Regular ticket type.
    - expect: A confirmation dialog appears asking whether the ticket should be added to the cart.
    - expect: The dialog has clear actions such as Cancel and Add.
    - expect: The cart counter/mini cart is not yet incremented until the add action is confirmed.
  3. Choose Add / confirm the dialog.
    - expect: The item is added to the cart.
    - expect: The cart counter increases to reflect the selected quantity.
    - expect: The user remains on the event page or is redirected to the mini cart/cart summary without losing the event details.

#### 1.4. 2.2 BUG - invalid quantities 0, negative, and very large are not blocked

**File:** `tests/events/02-invalid-quantity.spec.ts`

**Steps:**
  1. Starting state: fresh app, logged out. On /events/1/, enter 0 in the quantity field and click 'Buy tickets'.
    - expect: The app should show a validation error and prevent adding the item to the cart.
    - expect: The current behavior looks like a bug because the confirmation dialog still opens even for 0 and no clear validation message is displayed.
  2. Repeat with -1 and then with a very large number such as 999999.
    - expect: The app should reject invalid input and ask for a valid positive quantity.
    - expect: The current behavior looks like a bug because the same confirmation flow is triggered without validation, which can allow nonsensical cart quantities.

#### 1.5. 2.3 Cart counter and mini cart reflect the added item

**File:** `tests/events/03-cart-counter.spec.ts`

**Steps:**
  1. Starting state: fresh app, logged out. Add one or more tickets to the cart from an event page.
    - expect: The page updates to show the new cart count in the header.
    - expect: The mini cart, if present, reflects the selected item and quantity.
    - expect: The cart count matches the total quantity sum of all tickets in the cart.
  2. Navigate to /cart/ and inspect the cart contents.
    - expect: The just-added item appears with the correct event name, ticket type, quantity, and unit price.
    - expect: The cart count and total price are consistent with the selected quantities.

#### 1.6. 3.1 Cart page shows item details and total price

**File:** `tests/cart/01-cart-display.spec.ts`

**Steps:**
  1. Starting state: fresh app with one or more items in the cart. Open /cart/.
    - expect: The cart page heading is visible and the selected event item is listed.
    - expect: The event name, ticket type, quantity, and per-item price are shown.
    - expect: The total price updates correctly for the items in the cart.
  2. Add multiple ticket types or quantities to the cart and refresh the page.
    - expect: The cart total reflects each line item and the full order total.
    - expect: The displayed total corresponds to the selected quantities rather than a stale or default price.

#### 1.7. 3.2 Cart page allows changing quantity

**File:** `tests/cart/02-change-quantity.spec.ts`

**Steps:**
  1. Starting state: fresh app with an item in the cart. Open /cart/ and change the quantity from 1 to 3 on an item.
    - expect: The cart updates immediately or after saving changes.
    - expect: The line item quantity changes from 1 to 3.
    - expect: The total price recalculates to match the new quantity.
  2. Reduce the quantity to 0 or a negative value if the UI allows editing.
    - expect: The app should reject invalid values and either block the update or remove the item according to product rules.
    - expect: The current behavior should be checked for a validation error or an inconsistent total.

#### 1.8. 3.3 Cart page allows removing items and emptying cart

**File:** `tests/cart/03-remove-item.spec.ts`

**Steps:**
  1. Starting state: fresh app with at least two cart items. Open /cart/ and remove one item using the remove action.
    - expect: The item disappears from the cart list.
    - expect: The total price decreases accordingly.
    - expect: The remaining item still displays correct values.
  2. Remove the last remaining item.
    - expect: The cart page shows an empty-cart state.
    - expect: The cart count drops to 0 and the total price resets to zero or is hidden as appropriate.

#### 1.9. 4.1 Registration accepts valid credentials and creates an account

**File:** `tests/accounts/01-register-valid.spec.ts`

**Steps:**
  1. Starting state: fresh app, no active account for a new username. Open /register/ and create a user with a strong password.
    - expect: A new account is created successfully.
    - expect: The user is redirected to the login page or the account area with a confirmation message.
    - expect: The generated username appears in the app’s user-facing account flow.
  2. Use a valid password such as 'E2e-Pass-2026!' for the demo account or a similarly strong password.
    - expect: The registration form accepts the password and does not show a password policy error.
    - expect: The user can then log in with the new credentials.

#### 1.10. 4.2 Registration rejects weak or invalid passwords

**File:** `tests/accounts/02-register-invalid-password.spec.ts`

**Steps:**
  1. Starting state: fresh app, no active user with the target username. Open /register/ and submit a password that is too short, too common, or entirely numeric.
    - expect: The form should show a validation error and refuse registration.
    - expect: The app should keep the user on the form so they can correct the password.
  2. Attempt a password that matches the validation constraints incorrectly or is missing required confirmation.
    - expect: The form shows a clear error for the issue and does not create an account.
    - expect: The user remains on the registration page until the form is valid.

#### 1.11. 4.3 Login and logout for an existing user work as expected

**File:** `tests/accounts/03-login-logout.spec.ts`

**Steps:**
  1. Starting state: fresh app, not logged in. Open /accounts/login/ and log in as e2e_user / E2e-Pass-2026!.
    - expect: Authentication succeeds and the header changes to reflect the logged-in state.
    - expect: The user is redirected to a page consistent with the app flow, such as the homepage or a previous page.
  2. Logout from the header menu or account controls.
    - expect: The user is logged out successfully.
    - expect: The app no longer shows the logged-in state and the Login link is visible again.

#### 1.12. 4.4 Checkout and profile require login

**File:** `tests/accounts/04-login-gating.spec.ts`

**Steps:**
  1. Starting state: fresh app, logged out. Directly open /checkout/ and /profile/.
    - expect: The app should redirect unauthenticated users to the login screen or otherwise require login.
    - expect: The user should not be able to access the checkout or profile without authentication.
  2. After logging in, revisit /checkout/ and /profile/.
    - expect: Authenticated users can access the protected pages.
    - expect: The access requirements are enforced consistently for both routes.

#### 1.13. 5.1 Profile page shows recommendations after a purchase

**File:** `tests/profile/01-recommendations.spec.ts`

**Steps:**
  1. Starting state: logged in as e2e_user with a completed purchase in the cart or a recent order. Open /profile/.
    - expect: The profile page is visible and displays the user’s account information and purchase history.
    - expect: Recommended events appear after the purchase and are related to the event or category that was bought.
  2. Compare the recommendation list to the purchased event’s genre/category.
    - expect: At least one recommendation matches the same category or a closely related event.
    - expect: The recommendations are ordered or presented consistently and do not show unrelated items as the primary suggestion.

#### 1.14. 6.1 Contact form accepts valid data and submits successfully

**File:** `tests/contact/01-contact-success.spec.ts`

**Steps:**
  1. Starting state: fresh app, logged out. Open /contact/ and complete the form with a valid name, email, and message.
    - expect: The form accepts valid data without showing field-level errors.
    - expect: The user can click Send and the submission is accepted by the app or the form is reset with a success confirmation.
  2. Check the browser console or app response if this is a server-backed form.
    - expect: There is no validation error for correct input.
    - expect: The form behaves consistently for a real submission scenario.

#### 1.15. 6.2 Contact form validation errors are shown for invalid submissions

**File:** `tests/contact/02-contact-validation.spec.ts`

**Steps:**
  1. Starting state: fresh app, logged out. Open /contact/ and click Send without entering any data.
    - expect: The contact form shows validation messages for the required fields.
    - expect: The app does not submit the form with empty values.
  2. Enter an invalid email and incomplete fields, then submit again.
    - expect: The form clearly highlights the invalid input and requests corrections.
    - expect: The app keeps the user on the form until the data is valid.

#### 1.16. 7.1 How to buy page explains the purchase journey

**File:** `tests/static/01-how-to-buy.spec.ts`

**Steps:**
  1. Starting state: fresh app, logged out. Open /how-to-buy/.
    - expect: The page loads and contains the 'How to buy' instructions for the ticket purchase flow.
    - expect: The content explains that login is required for checkout and describes event selection, ticket choice, cart, and payment steps.
  2. Follow the page guidance to navigate to a valid event and to the cart if needed.
    - expect: The flow described in the page matches the real product flow.
    - expect: The user can reach event details and a cart from the site navigation without confusion.

#### 1.17. 7.2 BUG - unknown event page shows the Django debug 404 instead of a user-friendly error page

**File:** `tests/static/02-unknown-event-404.spec.ts`

**Steps:**
  1. Starting state: fresh app, logged out. Open /events/999/ or another non-existent event ID.
    - expect: The app should show a standard 404 page or a friendly 'event not found' message.
    - expect: A user should understand that the event does not exist without seeing a raw server traceback.
  2. Verify the page content and status.
    - expect: The current behavior looks like a bug because the app exposes a Django debug 404 page with stack-trace details in development mode.
    - expect: A production-grade solution should display a cleaner branded not-found page instead.

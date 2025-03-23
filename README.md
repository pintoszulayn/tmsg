## Debugging
1. **Find Queue Elements**: Open your target event page (e.g., `https://ticketmaster.sg/activity/detail/25sg_ladygaga`), press F12, and inspect the queue page (if present) for unique IDs or classes (e.g., `queue-it`, `queue-container`).
2. **Find Purchase URL**: After passing the queue manually, note the URL (e.g., `/tickets`) and update `bypass_queue`.
3. **Check Form Fields**: Inspect the checkout page for input field IDs (e.g., `cardNumber`, `expiry`) and update `checkout`.
4. **Run with Logs**: Use the logs to track progress and identify failures.

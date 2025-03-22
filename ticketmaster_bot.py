#!/usr/bin/env python3
"""Ticketmaster Bot CLI Entry Point

This script provides a command-line interface to run the Ticketmaster Bot,
allowing users to specify parameters like URL, proxy, and payment details.
"""

import argparse
from bot import TicketmasterBot

def main():
    """Parse CLI arguments and run the bot."""
    parser = argparse.ArgumentParser(description="Ticketmaster购票机器人")
    parser.add_argument("--url", required=True, help="目标Ticketmaster活动URL")
    parser.add_argument("--proxy", help="代理地址，例如 http://your_proxy:port")
    parser.add_argument("--captcha-key", help="2Captcha API密钥")
    parser.add_argument("--card-number", default="1234-5678-9012-3456", help="信用卡号")
    parser.add_argument("--expiry", default="12/25", help="信用卡有效期 (MM/YY)")
    parser.add_argument("--cvc", default="123", help="信用卡CVC码")

    args = parser.parse_args()

    bot = TicketmasterBot(
        url=args.url,
        proxy=args.proxy,
        captcha_key=args.captcha_key,
        card_number=args.card_number,
        expiry=args.expiry,
        cvc=args.cvc
    )
    bot.run()

if __name__ == "__main__":
    main()

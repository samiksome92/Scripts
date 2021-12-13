#!/usr/bin/env python3

"""A simple password generator.

Generates a secure random password of a given length using the secrets library. By default passwords include lowercase
letters, uppercase letters and digits, but not symbols. Options are provided to enable or disable any of the afore
mentioned sets. Additionally one can also provide a set of custom symbols.
"""

import argparse
import secrets
import string
import sys

import pyperclip

# Alphabets used for generation.
LOWERCASE = string.ascii_lowercase
UPPERCASE = string.ascii_uppercase
DIGITS = string.digits
SYMBOLS = string.punctuation


def main() -> None:
    """Main function for the script."""
    # Parse arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--length', help='Length of the generated password', type=int, default=15)
    parser.add_argument('-a', '--lowercase', help='Use lowercase letters', action='store_true')
    parser.add_argument('-na', '--no_lowercase', help="Don't use lowercase letters", action='store_true')
    parser.add_argument('-A', '--uppercase', help='Use uppercase letters', action='store_true')
    parser.add_argument('-nA', '--no_uppercase', help="Don't use uppercase letters", action='store_true')
    parser.add_argument('-1', '--digits', help='Use digits', action='store_true')
    parser.add_argument('-n1', '--no_digits', help="Don't use digits", action='store_true')
    parser.add_argument('-@', '--symbols', help='Use symbols', action='store_true')
    parser.add_argument('-n@', '--no_symbols', help="Don't use symbols", action='store_true')
    parser.add_argument('--valid_symbols', help='Provide a string of characters to use as symbols', default=None)
    parser.add_argument('-c', '--clipboard',
                        help='Copy generated password to clipboard instead of displaying it', action='store_true')
    args = parser.parse_args()

    # Validate arguments.
    if (
        args.lowercase and args.no_lowercase
        or args.uppercase and args.no_uppercase
        or args.digits and args.no_digits
        or args.symbols and args.no_symbols
        or args.no_symbols and args.valid_symbols
    ):
        print('ERROR: Conflicing arguments.')
        sys.exit(1)

    # Create list of valid characters.
    charsets = []
    if args.lowercase or not args.no_lowercase:
        charsets.append(LOWERCASE)
    if args.uppercase or not args.no_uppercase:
        charsets.append(UPPERCASE)
    if args.digits or not args.no_digits:
        charsets.append(DIGITS)
    if args.symbols or args.valid_symbols:
        charsets.append(args.valid_symbols if args.valid_symbols is not None else SYMBOLS)

    # Ensure charsets is not empty.
    if len(charsets) == 0:
        print('ERROR: Cannot generate password using empty character set.')
        sys.exit(1)

    # Generate password.
    while True:
        # First choose a set and then choose a character from the set.
        password = ''.join([secrets.choice(charsets[secrets.randbelow(len(charsets))]) for _ in range(args.length)])

        # Make sure password has at least one character from each set. Skip in case password length is shorter than
        # number of sets.
        if len(password) < len(charsets):
            break
        if LOWERCASE in charsets and not any([c in LOWERCASE for c in password]):
            continue
        if UPPERCASE in charsets and not any([c in UPPERCASE for c in password]):
            continue
        if DIGITS in charsets and not any([c in DIGITS for c in password]):
            continue
        if SYMBOLS in charsets and not any([c in SYMBOLS for c in password]):
            continue

        break

    # Display generated password or copy it to clipboard.
    if args.clipboard:
        pyperclip.copy(password)
    else:
        print(password)


if __name__ == '__main__':
    main()

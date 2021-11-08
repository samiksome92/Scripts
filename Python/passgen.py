#!/usr/bin/env python3

# TODO: Improve and add to README.md.

import argparse
import secrets
import string

# Alphabets used for generation.
LOWERCASE = string.ascii_lowercase
UPPERCASE = string.ascii_uppercase
DIGITS = string.digits


def main() -> None:
    """Main function for the script."""
    # Parse arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--length', help='Length of the generated password', type=int, default=15)
    args = parser.parse_args()

    # Generate password.
    while True:
        password = ''.join([secrets.choice(LOWERCASE+UPPERCASE+DIGITS) for _ in range(args.length)])

        # Make sure password has atleast one uppercase letter, one lowercase letter and one digit.
        if (
            any([c.isupper() for c in password])
            and any([c.islower() for c in password])
            and any([c.isdigit() for c in password])
        ):
            break

    # Display generated password.
    print(password)


if __name__ == '__main__':
    main()

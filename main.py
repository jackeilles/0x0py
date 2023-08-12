#!/usr/bin/env python3

import requests
import argparse
import tomllib
import os

URL = "https://0x0.st"
TERMS_PRIVACY = """
    Maximum file size: 512.0 MiB
    Not allowed: application/x-dosexec, application/x-executable, application/x-sharedlib, application/x-hdf5, application/java-archive, application/vnd.android.package-archive, application/x-rar, application/vnd.microsoft.portable-executable

    TERMS OF SERVICE
    ----------------

    0x0.st is NOT a platform for:
        * piracy
        * pornography and gore
        * extremist material of any kind
        * malware / botnet C&C
        * anything related to crypto currencies
        * backups (yes, this includes your minecraft stuff, seriously
        people have been dumping terabytes of it here for years)
        * CI build artifacts
        * doxxing, database dumps containing personal information
        * anything illegal under German law

    Uploads found to be in violation of these rules will be removed,
    and the originating IP address blocked from further uploads.

    Note that Tor exit nodes are blocked by the firewall due to frequent
    rule violations.

    PRIVACY POLICY
    --------------

    For the purpose of moderation, the following is stored with each
    uploaded file:
        * IP address
        * User agent string

    This site generally does not log requests, but may enable logging
    if necessary for purposes such as threat mitigation.

    No data is shared with third parties.
"""

def oneTimeSetup() -> None:

    # Does the config file already exist?
    if os.path.exists(os.path.expanduser("~/.0x0py")):
        # If so, check if the user has agreed to the terms
        with open(os.path.expanduser("~/.0x0py"), "rb") as f:
            dict = tomllib.load(f)
            if dict["termsAgree"]:
                # If so, go to main
                main()
                exit()         

    # If not, then do everything below

    # Make config file in home directory
    with open(os.path.expanduser("~/.0x0py"), "w") as f:
        f.write("""
# This checks whether the user has agreed to https://0x0.st's terms of service.
# Its also a checker to see if the first time setup has been run.
termsAgree = false
""")
        
    print(f"""

    Welcome to 0x0py! This is a simple command line tool to upload files to https://0x0.st.
    Please agree to the Terms of Service and Privacy Policy below.
          
    {TERMS_PRIVACY}

          """)
    
    # Ask user to agree to terms
    while True:
        termsAgree = input("Do you agree to the Terms of Service and Privacy Policy? (y/n): ")
        if termsAgree.lower() == "y":

            # Change config file to reflect that user has agreed to terms
            with open(os.path.expanduser("~/.0x0py"), "r") as f:
                contents = f.readlines()
                # Replace False with True
                for i, line in enumerate(contents):
                    if "termsAgree" in line:
                        contents[i] = "termsAgree = true\n"
                        break
                
            contents = [line for line in contents if termsAgree not in line]

            with open(os.path.expanduser("~/.0x0py"), "w") as f:
                f.writelines(contents)
                break

        elif termsAgree.lower() == "n":
            print("You must agree to the Terms of Service and Privacy Policy to use this tool.")
            exit()
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

    # Go to main
    main()


def parseArgs() -> argparse.Namespace:

    """
    Takes the command line arguments, 'file' being a required one, and parses them, then returns them to main().
    Dev Note: argparse isnt as bad as i remember - ArykDev xD
    """

    parser = argparse.ArgumentParser(
        prog="0x0py",
        description="A simple command line tool to upload files to https://0x0.st.",
        epilog="Made with blood, sweat, and tears by @ArykDev"
    )
    parser.add_argument("file", help="The file to upload.")
    parser.add_argument("-u", "--url", help="Upload a remote URL instead of a file.")

    args = parser.parse_args()

    return args

def post() -> str:

    """
    Final step! This function creates the POST request with the file and sends it off to 0x0.st
    If everything goes well, we'll recieve a response with the link to the file.
    """
    
    # Parse the command line arguments
    args = parseArgs()

    # Open the file in binary mode
    with open(args.file, "rb") as f:
        # Figure out file retention period using 0x0.st's formula
        retention = round(30 + (-365 + 30) * pow(((os.path.getsize(args.file) / 1048576) / 512 - 1), 3))
        # Make the POST request
        response = requests.post(URL, files={"file": f})
        # Print the response
        return response.text, retention


def main() -> None:
    response, retention = post()
    print(f"Your file has been uploaded to {response}")
    print(f"Your file will be deleted in approximately {retention} days.")
    
if __name__ == "__main__":
    oneTimeSetup()
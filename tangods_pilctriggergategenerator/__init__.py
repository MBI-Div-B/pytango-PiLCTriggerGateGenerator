from .PiLCTriggerGateGenerator import PiLCTriggerGateGenerator


def main():
    import sys
    import tango.server

    args = ["PiLCTriggerGateGenerator"] + sys.argv[1:]
    tango.server.run((PiLCTriggerGateGenerator,), args=args)

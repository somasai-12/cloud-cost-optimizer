import sys
import os

def main():
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))) 
        from src.cli import run_cli
        from src.config import check_configuration
        check_configuration()
        run_cli()
        
    except KeyboardInterrupt:
        print("\n\n✓ Key Board interrupt. Please restart!")
        sys.exit(0)
    except Exception as e:
        print(f"\n Fatal Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
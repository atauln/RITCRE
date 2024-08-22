import sys

class OutputManager:
    stdout = sys.stdout
    messages = []

    def start(self):
        sys.stdout = self
    
    def stop(self):
        sys.stdout = self.stdout
    
    def write(self, message):
        self.messages.append(message)
        self.stdout.write(message)
    
    def flush(self):
        self.stdout.flush()
    
    
    def get_messages(self):
        return self.messages
    
    def clear_messages(self):
        self.messages = []

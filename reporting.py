import os

class ReportGenerator:
    def __init__(self, output_directory: str):
        self.output_directory = output_directory
        if not os.path.exists(output_directory):
            os.makedirs(output_directory, exist_ok=True)

    def generate_report(self, stats, formats: list) -> list:
        return []

    def generate_summary(self, stats) -> str:
        s_dict = stats.to_dict()
        return f"\n{'='*30}\n📊 SONUÇ ÖZETİ\nBaşarılı Gönderim: {s_dict['success']}\nBaşarısız: {s_dict['failed']}\n{'='*30}\n"

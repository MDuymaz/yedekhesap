import requests
import logging
import re

class StreamUpdater:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://monotv524.com/'
        })

    def extract_domain_from_script(self, script_content):
        try:
            split_pattern = r"'([^']+)'.split\('\|'\)"
            match = re.search(split_pattern, script_content)
            if match:
                split_string = match.group(1)
                parts = split_string.split('|')
                domain_name = parts[3]
                domain_url = f"https://{domain_name}.com/domain.php"
                logging.info(f"Domain URL bulundu: {domain_url}")
                return domain_url
            return None
        except Exception as e:
            logging.error(f"Script parse hatası: {str(e)}")
            return None

    def get_domain_php_url(self):
        try:
            response = self.session.get('https://monotv524.com/channel?id=yayinzirve')
            if response.status_code != 200:
                logging.error("monotv523.com'a erişilemedi")
                return None

            script_pattern = r"eval\(function\(p,a,c,k,e,d\).*?split\('\|'\),0,{}\)\)"
            script_match = re.search(script_pattern, response.text, re.DOTALL)
            
            if script_match:
                return self.extract_domain_from_script(script_match.group(0))
            
            logging.error("Uygun script bulunamadı")
            return None

        except Exception as e:
            logging.error(f"domain.php URL'si alınamadı: {str(e)}")
            return None

    def get_new_domain(self):
        domain_php_url = self.get_domain_php_url()
        if not domain_php_url:
            return None

        try:
            response = self.session.get(domain_php_url)
            if response.status_code == 200:
                data = response.json()
                new_domain = data.get('baseurl', '').rstrip('/')
                return new_domain
            else:
                logging.error(f"Domain API yanıt vermedi. Status code: {response.status_code}")
        except Exception as e:
            logging.error(f"Yeni domain alınamadı: {str(e)}")
        return None

    def update_streams(self):
        new_domain = self.get_new_domain()
        if not new_domain:
            logging.error("Yeni domain alınamadı")
            return

        print(f"Güncel Domain: {new_domain}")

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    updater = StreamUpdater()
    updater.update_streams()

if __name__ == "__main__":
    main()

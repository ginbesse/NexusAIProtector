# NexusAIProtector

Bu proje, Termux üzerinde çalışan ve cihazı daha zor erişilir hale getiren, ağ kimliğini gizleyen ve sisteme entegre edilebilen güçlü bir koruma prototipidir.

## Özellikler
- Güvenlik taraması
- Kök erişim ve süper kullanıcı tespiti
- Ağ kimliği anonimleştirme
- Erişim zorluğu ve koruma katmanları
- Termux sistem kurulumu
- Sürekli koruma döngüsü

## Termux kurulumu
```bash
pkg update && pkg install -y python git curl

git clone <repo-url>
cd NexusAIProtector
bash install.sh
```

## Kurulum sonrası
```bash
python nexus_ai_protector.py install
nexus-ai-protector scan
nexus-ai-protector protect
```

## Not
Bu sürüm, gerçek dünya güvenlik ürünleri için bir çekirdek prototip olup, cihazın IP kimliğini gizleme ve erişimi zorlaştırma mantığını simüle eder.

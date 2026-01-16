# Hız Analiz Uygulaması

Video frame'leri üzerinde nokta seçerek hız ve mesafe hesaplamaları yapan modern bir masaüstü uygulaması.

## Kullanım

### 1. Video Yükleme
- "Video Yükle" butonuna tıklayın
- Video dosyanızı seçin (MP4, AVI, MOV, MKV)

### 2. Nokta Seçimi
- Ok tuşları (←→) ile frame'ler arasında gezinin
- "Nokta Seç" butonuna tıklayın
- Video üzerinde bir noktaya tıklayın
- İstediğiniz kadar nokta seçebilirsiniz (minimum 2)

### 3. Hesaplama
- "Hesapla" butonuna tıklayın
- Ardışık noktalar arası:
  - Mesafe (pixel, µm, mm)
  - Zaman (saniye)
  - Hız (µm/s, mm/s)
- Genel ortalama ve toplam değerler gösterilir
- Pixel oranı: 546 pixel = 1000 µm (sabit)

### 4. Sonuçları Kaydetme
- "Sonuçları CSV Olarak Kaydet" butonuna tıklayın
- Tüm hesaplamalar CSV formatında kaydedilir

## Klavye Kısayolları

| Tuş | İşlev |
|-----|-------|
| **F11** | Tam Ekran |
| **ESC** | Tam Ekrandan Çık |
| **←** | Önceki Frame |
| **→** | Sonraki Frame |
| **Home** | İlk Frame |
| **End** | Son Frame |
| **Page Up** | 10 Frame Geri |
| **Page Down** | 10 Frame İleri |

## Özellikler

✅ Modern ve kullanıcı dostu arayüz
✅ Video frame gezinme
✅ Çoklu nokta seçimi
✅ Otomatik hız ve mesafe hesaplama
✅ Genel ortalama ve toplam hesaplamalar
✅ CSV export
✅ Tam ekran modu
✅ Klavye kısayolları

## Gereksinimler

- Python 3.8+
- PyQt6
- OpenCV
- NumPy

## Örnek Kullanım

1. Video yükle (30 FPS)
2. Frame 5'te bir nokta seç
3. Frame 35'te bir nokta seç
4. Hesapla

**Sonuç:**
- Frame farkı: 30 frame
- Zaman: 1.0 saniye
- Hız ve mesafe otomatik hesaplanır

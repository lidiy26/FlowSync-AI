# FlowSync AI - Pilot Simülasyon Planı (MVP)

Bu plan, “en az ama çalışır” MVP’nin pilot/deneme mantığını tanımlar.

## 1) Senaryolar
- Sabah pik (ör. 08:00-10:00) ve etkinlik açık/kapalı
- Operatör eşiği artarken müdahale sayısının değişimi
- Yolcu nudging profilinin etkisi (Zamana duyarlı vs Zaman dengeli)

## 2) Ölçümler
- Occupancy homojenliği: occupancy std
- Bekleme proxy: aşım fazlasından türetilen değer
- Carbon proxy: ekstra sefer sayısı (extra_trip) + route_shift katsayısı

## 3) Geri bildirim
- Operatörün “kabul/reddet” oranı (MVP audit log’dan)
- Nudging mesajının kullanıcı tercihlerine etkisi (V1 kullanıcı geri bildirimiyle)


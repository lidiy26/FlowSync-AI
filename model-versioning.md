# FlowSync AI - Model Versiyonlama (V1 taslak)

MVP’de modeller “in-process” hesaplanıyor. V1+ için önerilen versiyonlama yaklaşımı:

## 1) Model Kimliği
- `model_name` (ör. `occupancy_regression`, `occupancy_gnn_baseline`)
- `model_version` (semver veya timestamp)
- `feature_schema_version`
- `training_dataset_version` (zaman aralığı + kaynaklar)

## 2) Yeniden Üretilebilirlik
- Her model, eğitim sırasında kullanılan hiperparametreleri ve rastgele tohumları saklamalı.
- Etkinlik/hava gibi dış sinyallerin snapshot’ı ile aynı koşullarda tekrar çalıştırabilmeli.

## 3) UI / Decision Engine Bağı
- `decision_engine` hangi model versiyonunu kullandığını her öneri çıktısına metadata olarak eklemeli.


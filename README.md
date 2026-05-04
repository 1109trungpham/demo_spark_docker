Setup Apache Iceberg bằng Docker là cách nhanh nhất để "vọc vạch" sức mạnh của định dạng bảng (table format) này mà không cần cấu hình Hadoop phức tạp.

Để có một môi trường Iceberg hoàn chỉnh, chúng ta sẽ cần 3 thành phần chính:

1. Compute Engine: Spark (để chạy các câu lệnh SQL/Dataframe).

2. Catalog: REST Catalog (để quản lý metadata/phiên bản của bảng).

3. Storage: MinIO (S3-compatible storage để lưu trữ file dữ liệu thực tế).


Iceberg hoạt động theo nguyên lý:
- Catalog (REST) = nguồn sự thật (metadata)
- MinIO (S3)     = nơi chứa file vật lý
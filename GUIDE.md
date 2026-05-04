
<!-- Click chuột phải vào GUIDE.md chọn Open Preview để nhìn tài liệu rõ hơn -->

Để có môi trường Data Lakehouse Iceberg hoàn chỉnh:
Tạo file `docker-compose.yml` chứa 3 thành phần sau:

1. `Compute Engine`: Spark (để chạy các câu lệnh SQL/Dataframe).
2. `Catalog`: REST Catalog (để quản lý metadata/phiên bản của Table).
3. `Storage`: MinIO (S3-compatible storage để lưu trữ file dữ liệu thực tế).


# Cấu trúc thư mục dự án:
```
demo_spark_docker/
├── minio_data/         # Nơi lưu trữ dữ liệu thực tế (Parquet, Metadata của Iceberg)
├── notebooks/          # Chứa các file Jupyter Notebook (.ipynb) để thử nghiệm
|   └── tutorials.ipynb
├── rest_catalog/       # Chứa Iceberg REST Catalog
├── .env                # File chứa các biến môi trường và version của image
├── docker-compose.yml  # File cấu trúc toàn bộ hạ tầng các container
├── GUIDE.md            # Tài liệu hướng dẫn sử dụng chi tiết
└── README.md         
```


# Khởi động hệ thống:

```bash
# Đứng tại thư mục gốc (demo_spark_docker) và chạy lệnh khởi động Docker Compose:
docker compose up -d
```

Đợi khoảng 30 giây để các service khởi động xong. Bạn có thể truy cập các địa chỉ sau:
- Jupyter Notebook: http://localhost:8888 (Nơi viết code Spark).
- MinIO Console: http://localhost:9001 (Đăng nhập với User: admin, Password: mypassword).
- Spark Master: http://localhost:8080.


### Bước 1: Truy cập giao diện MinIO (MinIO là Data Lake local - nơi bạn lưu dữ liệu của mình)
- Truy cập giao diện MinIO (http://localhost:9001)
- Một Bucket có tên là `warehouse` đã được tạo sẵn cho bạn (Bạn có thể tạo một cái mới trên giao diện nếu muốn).
- Dữ liệu MinIO được ánh xạ trong thư mục `minio_data` để bạn dễ quản lý (nếu bạn không muốn truy cập giao diện web).


### Bước 2: Chạy thử nghiệm với PySpark
- Truy cập vào Jupyter Notebook (http://localhost:8888),
- Đã có sẵn Notebook để bạn test.
- Jupyter Notebook của bạn trên giao diện cũng được ánh xạ vào thư mục `notebooks`.





# Dừng hệ thống:
- Đảm bảo bạn đã lưu các Notebook của mình trước khi dừng hệ thống (tránh mất code)
- Sau đó chạy lệnh:
```bash
docker compose down
```

Điều gì xảy ra sau đó:
- Dữ liệu, Notebook, Metadata của bạn đã được lưu trong các thư mục `minio_data`, `notebooks`, `rest_catalog` trên máy tính của bạn.
- Sau này bạn khởi động lại hệ thống với lệnh `docker compose up -d` thì các thư mục trên sẽ được ánh xạ vào môi trường Docker -> nên mọi thứ vẫn còn nguyên.





# Xóa dữ liệu và bucket
(làm theo thứ tự để tránh xung đột metadata sau này, có thể không làm bước 3)

Bạn cần hiểu Phân cấp trong Lakehouse Iceberg để biết mình thực sự đang xóa cái gì:
```
Catalog
 └── Namespace (database/schema)
      └── Table
```

### Bước 1. Xóa Table
```python
# Chạy lệnh xóa Table (có PURGE: xoá data + metadata):
spark.sql("DROP TABLE IF EXISTS my_catalog.my_namespace.my_table PURGE")
```
Lưu ý: Từ khóa `PURGE` rất quan trọng. Nếu không có PURGE, Iceberg có thể chỉ xóa metadata còn file dữ liệu vẫn nằm "vất vưởng" trên MinIO.


### Bước 2. Xóa Namespace(database/schema)
```python
spark.sql("DROP NAMESPACE IF EXISTS my_catalog.my_namespace")
```
Thêm `CASCADE` phía sau lệnh nếu bạn muốn xóa toàn bộ Table trong Namespace đó.


Lưu ý: Không có lệnh SQL để xóa `Catalog`

Vì Catalog là:
- một config trong Spark
- hoặc một service bên ngoài (REST - thứ chúng ta đang dùng)

Trong trường hợp của chúng ta thì Catalog đang nằm trong container REST, nếu bạn muốn reset toàn bộ:
1. Chạy lệnh `docker compose down -v` (-> xoá metadata catalog + state của REST service).
2. Xóa file `catalog.db` trong thư mục `rest_catalog` trên máy tính của bạn.

Bạn có thể không xoá dữ liệu trong thư mục `minio_data`, nhưng sau này bạn chạy lại hệ thống mới thì Spark sẽ không còn "nhìn thấy" dữ liệu cũ đó nữa, vì bạn đã xóa metadata của nó. (Bạn có thể tìm hiểu thêm về lý do, nhưng cơ bản là file `catalog.db` rất quan trọng để Spark có thể tìm và hiểu data mà nó xử lý)

### Bước 3. Xóa Bucket trong MinIO

- Cách 1
```bash
# Chạy lệnh xem network:
docker network ls
# Output trên máy bạn có thể là: demo_spark_docker_iceberg_net
# dùng tên network này để chạy lệnh phía dưới

# Ví dụ muốn xóa Bucket tên là warehouse: 
docker run --rm \
  --network demo_spark_docker_iceberg_net \
  --entrypoint /bin/sh \
  minio/mc -c "
    mc alias set minio http://minio:9000 admin mypassword &&
    mc rm --recursive --force --versions minio/warehouse &&
    mc rb minio/warehouse
  "
```

- Cách 2
```bash
docker exec minio mc alias set local http://localhost:9000 admin mypassword
docker exec minio mc rb --force local/warehouse
```

### Terraform을 이용한 GKE 구성
1. 해당 git을 clone하여 terraform.tfvars의 값을 적절히 수정
2. terraform 명령어를 이용해 GKE 구성
```
terraform init
terraform plan
terraform apply
```
	주의점 : location을 처음에는 asia-northeast3(서울)로 하였으나, 해당지역에 설정된 SSD 총 사용량 한도를 초과했다는 오류가 있었고, 리소스 여유가 있는 지역으로 다시 생성을 진행하였습니다. (머신 타입도 더 좋은 걸로 바꿨습니다.)

### Helm을 이용한 Airflow Deploy
1. gcloud shell에 접속합니다.
2. helm repo를 추가합니다.
```
helm repo add apache-airflow https://airflow.apache.org
helm repo update
```
3. airflow를 배포합니다.
```
helm install airflow apache-airflow/airflow --debug
```
4. 로컬에서 ssh key 생성합니다.
```
ssh-keygen -t rsa -b 4096 -C "{id}@{domain}.com"

```
5. git repository에 ssh key를 등록합니다
	- target git repository 접속 -> Settings -> Deploy keys -> Add deploy key
```
# 클립보드로 key 복사 (id_rsa.pub을 복사)
pbcopy < {id_rsa.pub 파일 위치}

# 등록 후, test (ids_rsa를 이용하여 테스트, pub 아님)
ssh -i {id_rsa 파일 위치} git@github.com
```
6. 로컬에서 gcloud로 생성된 id_rsa key를 전송합니다.
```
gcloud cloud-shell scp localhost:{id_rsa 경로} cloudshell:~/id_rsa
```
7. gcloud shell에서 필요한 secret을 생성합니다.
```
// ssh 접속을 위한 secret 생성
kubectl create secret generic git-ssh-key --from-file=gitSshKey=./id_rsa

// webserver secret 생성
kubectl create secret generic airflow-webserver-secret --from-literal="webserver-secret-key=$(python3 -c 'import secrets; print(secrets.token_hex(16))')"
```
8. values.yaml 파일을 가져와 수정합니다.
```
helm show values apache-airflow/airflow > values.yaml
```
9. values.yaml 파일 내 다음 부분들을 수정합니다.
```
webserverSecretKeySecretName: "airflow-webserver-secret"
webserver:
  service:
    type: "LoadBalancer"
gitSync:
  enabled: true
  repo: {git repository의 ssh}
  branch: {git branch명}
  rev: HEAD
  subPath: {git repository 내 dag를 가져올 경로}
  sshKeySecret: "git-ssh-key"
```
10. 새로운 values.yaml 파일로 업데이트합니다.
```
helm upgrade airflow apache-airflow/airflow --values values.yaml --debug
```
11. external IP를 확인하여 airflow webserver에 접근 가능합니다.
```
kubectl get all

# {external_ip}:8080으로 접속
```
### 허용된 IP만 접속 가능하도록 수정


### 참고
- https://mjs1995.tistory.com/296

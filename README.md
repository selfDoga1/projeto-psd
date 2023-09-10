
# Projeto PSD

Um projeto da cadeira de Projeto de Sistemas Distribuídos


## Requisitos de utilização

- [zerotier](https://www.zerotier.com/) cria uma rede lan entre os computadores;
- [pasta com os vetores](https://drive.google.com/drive/folders/1l1-ILjj8zMn4NTJPH1ZeZO93k_1jfqpm?usp=sharing) a serem calculados
- [python](https://www.python.org/) linguagem de programação utilizada no projeto.
- bibliotecas necessarias no requirements.txt
## Utilização
- No projeto existem 3 tipos de scripts que representam 3 métodos abordados.
    - O primeiro método representa a variação P1.
    - O segundo método representa a variação P2 até P4.
    - O terceiro método representa a variação P5.

- No primeiro e segundo método para a escolha dos vetores a serem multiplicados basta editar a linha:

    ```python
    self.matrix_1 = Matrix(f'{current_dir}/src/<nome_do_arquivo>.txt')
    self.matrix_2 = Matrix(f'{current_dir}/src/<nome_do_arquivo>.txt')
    ```

- No Segundo método para a escolha do numero de threads basta editar a linha:
    ```python 
    THREADS_AMOUNT = <numero de threads que deseja>
    ```

- Já no terceiro método é necessário seguir os segunites passos:
    - Configuração do zerotier em todos os computadores e conectar todos na mesma rede.
    - No terceiro método temos temo 3 "entidades", sendo elas:
        - **Client**: solicita ao server o processamento das matrizes.
        - **Worker**: responsável pelo cálculo das matrizes.
        - **Server**: responsável por distribuir o trabalho para os **Workers** e retornar o resultado para o **Client**.

    - Será necessario configurar o arquivo .env e colocalo na raiz do projeto de acordo com os IPs que o zerotier fornecer:
        ```bash 
        SERIALIZER = 'json'
        SERVER_NAME = 'Server'
        SERVER_HOST = '172.27.251.50'
        SERVER_PORT = '9090'
        WORKER_NAME = 'Worker'
        WORKER_HOST = '172.27.251.50'
        ```
        - Troque o SERVER_HOST e WORKER_HOST de acordo com os computadores utilizados.
        - Não é necessário trocar o SERVER_NAME e WORKER_NAME.


    - Primeiro é necessário iniciar o servidor em um dos computadores:
        ```bash 
            python server.py
        ```
    
    - Logo após iniciar os workers:
        ```bash 
            python worker.py
        ```
        - o **Worker** pode ser iniciado em mais de um computador, para o funcionamento o IP do servidor deverá ser o mesmo para todos os **Workers**.
        - Ao iniciar um **Worker** o mesmo se comunica com servidor, assim o servidor dividirá a tarefa para cada um.

    - Ao final iniciar o client, porém configurar o caminho das matrizes editano as linhas:
        ```python 
        matrix_1 = load_matrix('<nome_do_arquivo>.txt')
        matrix_2 = load_matrix('<nome_do_arquivo>.txt')

        ```

    

## Autor

- [@DouglasCostaBezerra](https://github.com/selfDoga1)


# Projeto de Desenho com Dedo Indicador

Este projeto utiliza a tecnologia de detecção de mãos e marcadores do MediaPipe, juntamente com OpenCV, para permitir que o usuário desenhe na tela utilizando a posição do dedo indicador de uma ou mais mãos. O código também permite alterar a cor, a espessura do desenho e utilizar uma borracha para apagar.

## Funcionalidades

- **Desenho com a mão**: O usuário pode desenhar na tela utilizando a posição do dedo indicador de uma ou mais mãos.
- **Controle de espessura e cor**: A espessura e a cor do desenho podem ser ajustadas em tempo real.
- **Borracha**: O usuário pode ativar o modo de borracha pressionando o botão direito do mouse.
- **Máscara de fundo**: O desenho é aplicado sobre uma máscara para não interferir no fundo da imagem.

## Tecnologias

- **Python** 3.8
- **OpenCV**: Para manipulação de imagens e vídeos em tempo real.
- **MediaPipe**: Para detecção de mãos e pontos-chave.

## Como Rodar

### Pré-requisitos

Certifique-se de ter o Python 3.x instalado. Além disso, instale as dependências do projeto utilizando o `pip`:

### Instalação

1. Clone o repositório:

    ```bash
    git clone https://github.com/seu_usuario/seu_repositorio.git
    cd seu_repositorio
    ```

2. Instale as dependências:

    ```bash
    pip install -r requirements.txt
    ```

3. Execute o aplicativo:

    ```bash
    python app/main.py
    ```

4. O aplicativo irá abrir a câmera e você pode interagir com o desenho utilizando sua mão.

### Controle de Cores e Espessura

- Use as barras de controle para ajustar a espessura e a cor do desenho.
- Para ativar a borracha, clique com o botão direito do mouse.

### Fechar o aplicativo

- Para fechar o aplicativo, pressione a tecla `q`.
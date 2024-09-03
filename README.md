# API de Conversão de Dados de Planilha / Spreadsheet Data Conversion API

## Sumário / Table of Contents

- [Português](#português)
  - [Descrição](#descrição)
  - [Objetivo e Funcionalidade](#objetivo-e-funcionalidade)
  - [Como Utilizar](#como-utilizar)
    - [Instalação](#instalação)
    - [Inicialização do App Flask](#inicialização-do-app-flask)
    - [Rotas Disponíveis](#rotas-disponíveis)
- [English](#english)
  - [Description](#description)
  - [Purpose and Functionality](#purpose-and-functionality)
  - [How to Use](#how-to-use)
    - [Installation](#installation)
    - [Starting the Flask App](#starting-the-flask-app)
    - [Available Routes](#available-routes)

---

## Português

### Descrição

Esta API é um algoritmo de conversão de dados de uma planilha para um banco de dados relacional ou não relacional. O algoritmo funciona lendo arquivos no formato `.xlsx` (apenas `.xlsx`), transformando-os em um dataframe e, posteriormente, em um array de objetos.

### Objetivo e Funcionalidade

A API serve como uma "Estação de Tratamento", onde o cliente insere uma planilha e a envia para essa API. A API se encarrega de processar e enviar os dados de forma correta para uma API server-side. O objetivo é oferecer uma opção leve e de baixa latência para o processamento de dados relacionados a planilhas.

**Atenção:** O algoritmo utiliza threads e o conceito de batch requests com payloads para otimizar o tempo de processamento, especialmente em cenários com alto volume de dados. É importante que a API que recebe esses dados (via POST, por exemplo) tenha uma lógica preparada para lidar com a inserção de payloads. **Dica:** Bulk inserts e paralelismo são bastante úteis nesse contexto.

### Como Utilizar

#### Instalação

1. **Crie uma virtual environment (venv) e baixe as dependências do projeto.**  
   **OBS:** Verifique se o Python instalado em sua máquina é igual ou superior à versão 3.12.

   - Criação da venv:
     ```bash
     python -m venv <nome_da_venv>
     ```
   - Ativação:
     - MacOS/Linux:
       ```bash
       source <nome_da_venv>/bin/activate
       ```
     - Windows:
       ```bash
       <nome_da_venv>\scripts\activate
       ```
   - Instalação das dependências:
     ```bash
     pip install -r requirements.txt
     ```

#### Inicialização do App Flask

   Para inicializar a aplicação Flask, execute o seguinte comando:
   ```bash
   flask run
   ```

#### Rotas Disponíveis
  A api consta com uma única rota via POST:
  ```bash
  <api-domain>/format
  ```


---

## Description

This API is an algorithm for converting data from a spreadsheet into a relational or non-relational database. The algorithm works by reading `.xlsx` files (only `.xlsx`), transforming them into a dataframe, and then into an array of objects.

## Purpose and Functionality

The API serves as a "Treatment Station," where the client uploads a spreadsheet and sends it to this API, which is responsible for processing and correctly sending the data to a server-side API. The goal is to provide a lightweight, low-latency option for processing spreadsheet-related data.

**Attention:** The algorithm uses threads and the concept of batch requests with payloads to optimize processing time, especially in scenarios with high data volumes. It is important that the receiving API (via POST, for example) has logic in place to handle payload inserts. **Tip:** Bulk inserts and parallelism are very useful in this context.

## How to Use

### Installation

1. **Create a virtual environment (venv) and install the project dependencies.**  
   **Note:** Ensure that the Python version installed on your machine is 3.12 or higher.

   - Create the venv:
     ```bash
     python -m venv <venv_name>
     ```
   - Activate the venv:
     - MacOS/Linux:
       ```bash
       source <venv_name>/bin/activate
       ```
     - Windows:
       ```bash
       <venv_name>\scripts\activate
       ```
   - Install the dependencies:
     ```bash
     pip install -r requirements.txt
     ```

### Starting the Flask App

   To start the Flask application, run the following command:
   ```bash
   flask run
   ```
### Available Routes
  The api has a single route via POST:
  ```bash
  <api-domain>/format
  ```

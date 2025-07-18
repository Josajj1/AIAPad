# AIAPad - Sistema de Análise de Lâminas Anatomopatológicas

**Versão:** 1.0.0  
**Data:** 15 de Julho de 2025  
**Autor:** Manus AI  
**Domínio:** lip.fm.usp.br  
**IP do Servidor:** 143.107.178.21  

---

## Resumo Executivo

O AIAPad (Artificial Intelligence Anatomopathological Pad) representa uma solução tecnológica inovadora desenvolvida especificamente para revolucionar a análise de lâminas anatomopatológicas através da integração de inteligência artificial, processamento de imagens avançado e uma interface web intuitiva. Este sistema foi concebido para atender às necessidades crescentes de laboratórios de patologia, instituições de ensino médico e centros de pesquisa que demandam ferramentas eficientes para o diagnóstico assistido por computador.

A plataforma oferece uma abordagem abrangente para o gerenciamento e análise de lâminas digitalizadas, incorporando funcionalidades avançadas de machine learning para detecção automática de doenças, reconhecimento de reagentes e colorações, além de um sistema robusto de anotações colaborativas que facilita o processo de ensino e aprendizado em patologia. O sistema foi desenvolvido com foco na escalabilidade, segurança e facilidade de uso, garantindo que profissionais de diferentes níveis de experiência técnica possam utilizar efetivamente suas funcionalidades.

O AIAPad distingue-se por sua capacidade de processar arquivos de lâminas de até 5GB, suportando os principais formatos utilizados por scanners comerciais, incluindo SVS, TIFF, NDPI, SCN, MRXS, VMS e VMU. Esta versatilidade garante compatibilidade com equipamentos de diferentes fabricantes, eliminando barreiras técnicas que frequentemente limitam a adoção de soluções digitais em laboratórios de patologia.

A arquitetura do sistema foi projetada para facilitar a instalação e manutenção, incluindo scripts automatizados que permitem a implantação completa em servidores Debian/Ubuntu com um único comando. Esta abordagem reduz significativamente o tempo e a complexidade tradicionalmente associados à implementação de sistemas de patologia digital, tornando a tecnologia mais acessível para instituições de diferentes portes.

## Introdução e Contexto

A patologia digital representa uma das áreas de maior crescimento na medicina moderna, impulsionada pela necessidade de diagnósticos mais precisos, eficientes e acessíveis. A digitalização de lâminas histopatológicas não apenas preserva amostras valiosas, mas também possibilita a aplicação de técnicas avançadas de análise computacional que podem identificar padrões sutis frequentemente imperceptíveis ao olho humano.

O desenvolvimento do AIAPad surge em resposta às limitações identificadas em soluções existentes, que frequentemente apresentam interfaces complexas, compatibilidade limitada com diferentes formatos de arquivo, ou custos proibitivos para instituições menores. Nossa abordagem prioriza a democratização do acesso à tecnologia de ponta em patologia digital, oferecendo uma solução completa, open-source e facilmente implementável.

A integração de inteligência artificial no processo diagnóstico representa um paradigma fundamental na medicina contemporânea. Estudos recentes demonstram que sistemas de IA podem alcançar níveis de precisão comparáveis ou superiores aos de patologistas experientes em tarefas específicas, particularmente na detecção de câncer e classificação de lesões. O AIAPad incorpora estes avanços através de modelos de deep learning especificamente treinados para análise histopatológica, oferecendo suporte diagnóstico em tempo real.

A plataforma foi desenvolvida considerando os desafios únicos enfrentados por laboratórios de patologia, incluindo a necessidade de gerenciar grandes volumes de dados, garantir a segurança e privacidade das informações médicas, e facilitar a colaboração entre profissionais geograficamente distribuídos. O sistema de anotações colaborativas permite que múltiplos especialistas contribuam para o processo diagnóstico, criando um ambiente de aprendizado contínuo e melhoria da qualidade diagnóstica.

## Arquitetura do Sistema

### Visão Geral da Arquitetura

O AIAPad foi desenvolvido seguindo uma arquitetura moderna de três camadas, separando claramente as responsabilidades entre apresentação, lógica de negócio e persistência de dados. Esta abordagem garante escalabilidade, manutenibilidade e flexibilidade para futuras expansões do sistema.

A camada de apresentação é implementada através de uma Single Page Application (SPA) desenvolvida em React, oferecendo uma interface responsiva e intuitiva que se adapta a diferentes dispositivos e tamanhos de tela. A utilização de tecnologias modernas como Tailwind CSS e shadcn/ui garante uma experiência de usuário consistente e profissional, enquanto a arquitetura baseada em componentes facilita a manutenção e extensão da interface.

A camada de lógica de negócio é implementada através de uma API RESTful desenvolvida em Flask, oferecendo endpoints bem definidos para todas as funcionalidades do sistema. Esta abordagem permite a integração com sistemas externos e facilita o desenvolvimento de aplicações cliente adicionais. A API incorpora padrões de segurança modernos, incluindo autenticação JWT, rate limiting e validação rigorosa de entrada.

A camada de persistência utiliza SQLite para armazenamento de metadados e informações estruturadas, complementada por um sistema de arquivos otimizado para o armazenamento de lâminas digitalizadas. Esta combinação oferece performance adequada para a maioria dos casos de uso, mantendo a simplicidade de implantação e manutenção.

### Componentes Principais

#### Backend Flask

O backend do AIAPad é construído sobre o framework Flask, escolhido por sua flexibilidade, simplicidade e extensibilidade. A estrutura modular do código facilita a manutenção e permite a adição de novas funcionalidades sem impactar componentes existentes.

O sistema de roteamento é organizado em blueprints temáticos, incluindo autenticação, gerenciamento de usuários, processamento de lâminas, upload de arquivos e monitoramento do sistema. Cada blueprint encapsula funcionalidades relacionadas, promovendo a separação de responsabilidades e facilitando o desenvolvimento colaborativo.

A integração com bibliotecas especializadas como OpenSlide permite o processamento eficiente de lâminas digitalizadas, incluindo extração de metadados, geração de thumbnails e criação de tiles para visualização em diferentes níveis de zoom. O sistema suporta nativamente os principais formatos utilizados por scanners comerciais, garantindo compatibilidade ampla com equipamentos existentes.

#### Frontend React

A interface do usuário é implementada como uma aplicação React moderna, utilizando hooks e context API para gerenciamento de estado. A arquitetura baseada em componentes funcionais promove a reutilização de código e facilita a manutenção.

O sistema de roteamento client-side permite navegação fluida entre diferentes seções da aplicação, enquanto o lazy loading de componentes otimiza o tempo de carregamento inicial. A integração com bibliotecas de UI modernas garante uma experiência visual consistente e profissional.

O visualizador de lâminas incorpora funcionalidades avançadas de zoom, pan e anotação, implementadas através de canvas HTML5 para máxima performance. O sistema de anotações permite a criação de marcações precisas que são sincronizadas em tempo real com o backend.

#### Sistema de Banco de Dados

O modelo de dados foi projetado para suportar eficientemente as operações típicas de um sistema de patologia digital, incluindo gerenciamento de usuários, metadados de lâminas, anotações e resultados de análises de IA.

A estrutura de usuários suporta diferentes tipos de perfis (administradores, médicos, pesquisadores, estudantes), cada um com permissões específicas que controlam o acesso a funcionalidades e dados. O sistema de autenticação baseado em JWT garante segurança adequada enquanto mantém performance otimizada.

Os metadados de lâminas incluem informações técnicas extraídas automaticamente durante o upload, como dimensões, níveis de zoom disponíveis, tipo de scanner utilizado e coloração detectada. Estas informações são utilizadas para otimizar a visualização e análise das lâminas.

### Integração de Componentes

A comunicação entre frontend e backend é realizada através de uma API RESTful bem definida, utilizando JSON para troca de dados. O sistema de autenticação baseado em tokens JWT permite sessões seguras e escaláveis, enquanto o middleware de CORS facilita o desenvolvimento e deployment em diferentes ambientes.

O sistema de cache implementado com Redis (com fallback para memória) otimiza a performance através do armazenamento temporário de dados frequentemente acessados, incluindo metadados de lâminas, tiles de visualização e resultados de análises de IA.

O monitoramento integrado coleta métricas de performance e saúde do sistema, oferecendo endpoints específicos para integração com ferramentas de monitoramento externas como Prometheus e Grafana.




## Funcionalidades Principais

### Sistema de Upload e Processamento de Lâminas

O sistema de upload do AIAPad foi desenvolvido para lidar eficientemente com arquivos de lâminas digitalizadas de grande porte, suportando arquivos de até 5GB através de uma implementação robusta de upload chunked. Esta abordagem divide arquivos grandes em segmentos menores que são transmitidos independentemente, permitindo a retomada de uploads interrompidos e melhorando a confiabilidade geral do processo.

O processo de upload inicia com uma fase de validação que verifica a integridade e formato do arquivo antes da transmissão completa. O sistema utiliza magic numbers e análise de cabeçalho para identificar automaticamente o formato da lâmina, garantindo compatibilidade com os principais scanners comerciais. Durante esta fase, são extraídos metadados preliminares que informam o usuário sobre as características básicas da lâmina.

A transmissão dos dados é realizada através de chunks de 1MB, cada um acompanhado de checksums MD5 para verificação de integridade. O sistema mantém um registro detalhado do progresso de upload, permitindo que usuários monitorem o status em tempo real através de uma interface de progresso dinâmica. Em caso de interrupção, o sistema pode retomar o upload a partir do último chunk transmitido com sucesso.

Após a transmissão completa, o sistema executa uma fase de processamento que inclui a montagem dos chunks, verificação final de integridade e extração completa de metadados. Utilizando a biblioteca OpenSlide, o sistema extrai informações técnicas detalhadas incluindo dimensões da lâmina, níveis de magnificação disponíveis, resolução em microns por pixel, e características específicas do scanner utilizado.

O reconhecimento automático de coloração é realizado através de análise de histograma de cores e padrões característicos de diferentes reagentes. O sistema pode identificar colorações comuns como Hematoxilina e Eosina (H&E), PAS, Tricrômico de Masson, e diversas colorações imunohistoquímicas. Esta informação é crucial para a aplicação de algoritmos de análise específicos para cada tipo de coloração.

### Visualização Avançada de Lâminas

O visualizador de lâminas do AIAPad oferece uma experiência de navegação fluida e intuitiva, implementada através de tecnologias web modernas que garantem performance adequada mesmo para lâminas de alta resolução. O sistema utiliza uma abordagem de tiles piramidais que permite zoom suave desde visões panorâmicas até magnificações celulares detalhadas.

A interface de visualização incorpora controles intuitivos para navegação, incluindo zoom através de mouse wheel, pan através de drag-and-drop, e navegação rápida através de um mini-mapa que oferece contexto espacial durante a exploração detalhada. O sistema mantém a qualidade visual através de algoritmos de interpolação avançados que garantem nitidez em todos os níveis de zoom.

As funcionalidades de medição permitem que usuários realizem medições precisas de estruturas anatômicas, com conversão automática entre pixels e unidades métricas baseada nos metadados de resolução da lâmina. O sistema oferece ferramentas para medição de distâncias, áreas e perímetros, com resultados apresentados em unidades apropriadas para análise patológica.

O sistema de anotações integrado permite a criação de marcações precisas diretamente sobre a lâmina, incluindo pontos de interesse, regiões retangulares e circulares, e anotações de forma livre. Cada anotação pode incluir texto descritivo, classificação categórica e metadados adicionais que facilitam a organização e busca posterior.

### Inteligência Artificial e Análise Automatizada

O módulo de IA do AIAPad incorpora algoritmos de deep learning especificamente treinados para análise histopatológica, oferecendo suporte diagnóstico em diversas especialidades médicas. O sistema utiliza redes neurais convolucionais (CNNs) otimizadas para processamento de imagens médicas, com arquiteturas adaptadas para diferentes tipos de análise.

A detecção automática de doenças é implementada através de modelos ensemble que combinam múltiplas arquiteturas de rede neural para maximizar a precisão diagnóstica. O sistema pode identificar padrões característicos de diversas condições patológicas, incluindo neoplasias, processos inflamatórios e alterações degenerativas. Os resultados são apresentados com níveis de confiança quantificados, permitindo que profissionais avaliem adequadamente as sugestões do sistema.

O reconhecimento de estruturas anatômicas utiliza técnicas de segmentação semântica para identificar e delimitar diferentes componentes teciduais. Esta funcionalidade é particularmente útil para análises quantitativas, permitindo medições automáticas de densidade celular, proporções teciduais e distribuição espacial de estruturas específicas.

O sistema de classificação de coloração emprega algoritmos de análise espectral para identificar automaticamente o tipo de reagente utilizado na preparação da lâmina. Esta informação é crucial para a aplicação de algoritmos de análise específicos e para a normalização de cores que compensa variações técnicas entre diferentes laboratórios.

A análise de regiões de interesse (ROI) permite que usuários definam áreas específicas para análise detalhada, com o sistema aplicando algoritmos especializados para extrair características quantitativas relevantes. Os resultados incluem métricas morfométricas, índices de proliferação celular e scores de intensidade de coloração.

### Sistema de Autenticação e Autorização

O sistema de segurança do AIAPad implementa múltiplas camadas de proteção para garantir a confidencialidade e integridade dos dados médicos. A autenticação é baseada em tokens JWT (JSON Web Tokens) que oferecem segurança robusta mantendo performance otimizada para aplicações web.

O modelo de usuários suporta quatro tipos principais de perfis, cada um com permissões específicas adaptadas às necessidades de diferentes profissionais. Administradores possuem acesso completo ao sistema, incluindo gerenciamento de usuários, configurações globais e monitoramento de performance. Médicos têm acesso a funcionalidades diagnósticas completas, incluindo análise de IA e criação de relatórios. Pesquisadores podem acessar dados agregados e ferramentas de análise estatística, enquanto estudantes têm acesso limitado focado em funcionalidades educacionais.

O sistema de sessões mantém controle detalhado sobre atividades de usuários, incluindo logs de acesso, histórico de visualizações e registro de anotações criadas. Esta informação é crucial para auditoria e compliance com regulamentações de privacidade médica.

A implementação de rate limiting protege o sistema contra abuso e ataques de negação de serviço, com limites específicos para diferentes tipos de operações. Operações de autenticação têm limites mais restritivos para prevenir ataques de força bruta, enquanto operações de visualização têm limites mais permissivos para não impactar a experiência do usuário.

### Gerenciamento de Dados e Backup

O sistema de gerenciamento de dados do AIAPad foi projetado para garantir a integridade, disponibilidade e recuperabilidade das informações médicas armazenadas. A estratégia de backup implementa múltiplas camadas de proteção, incluindo backups incrementais diários, snapshots semanais e arquivamento mensal de longo prazo.

O sistema de versionamento mantém histórico completo de alterações em lâminas e anotações, permitindo a recuperação de estados anteriores quando necessário. Esta funcionalidade é particularmente importante em ambientes de pesquisa onde a rastreabilidade de mudanças é crucial para a validade científica dos resultados.

A compressão inteligente de dados reduz significativamente os requisitos de armazenamento sem comprometer a qualidade das imagens. O sistema utiliza algoritmos de compressão sem perda para regiões críticas e compressão com perda controlada para áreas menos relevantes, otimizando o equilíbrio entre qualidade e eficiência de armazenamento.

O monitoramento contínuo de integridade verifica regularmente a consistência dos dados armazenados, detectando e corrigindo automaticamente problemas menores. Alertas são gerados para administradores quando problemas mais sérios são detectados, permitindo intervenção rápida antes que afetem usuários finais.

## Instalação e Configuração

### Requisitos do Sistema

O AIAPad foi desenvolvido para operar eficientemente em servidores Linux modernos, com requisitos de hardware dimensionados para suportar cargas de trabalho típicas de laboratórios de patologia. Os requisitos mínimos incluem um processador multi-core de 64 bits, 4GB de RAM e 50GB de espaço em disco, embora configurações mais robustas sejam recomendadas para ambientes de produção com múltiplos usuários simultâneos.

O sistema operacional deve ser Debian 10 ou superior, ou Ubuntu 18.04 LTS ou superior, garantindo compatibilidade com bibliotecas e dependências necessárias. A escolha por distribuições baseadas em Debian facilita a manutenção e garante estabilidade de longo prazo, características essenciais para sistemas médicos críticos.

A conectividade de rede deve suportar HTTPS para garantir a segurança na transmissão de dados médicos sensíveis. O sistema requer acesso às portas 80 e 443 para operação normal, com configuração automática de certificados SSL através do Let's Encrypt.

### Processo de Instalação Automatizada

O processo de instalação do AIAPad foi simplificado através de scripts automatizados que executam todas as etapas necessárias com intervenção mínima do administrador. O script principal `install.sh` detecta automaticamente a distribuição Linux, instala dependências necessárias e configura todos os componentes do sistema.

A instalação inicia com a atualização do sistema operacional e instalação de dependências básicas, incluindo compiladores, bibliotecas de desenvolvimento e ferramentas de rede. O script então procede com a instalação do Python 3.11 e Node.js 20, versões específicas testadas para compatibilidade ótima com o AIAPad.

A configuração do ambiente Python inclui a criação de um ambiente virtual isolado e instalação de todas as dependências especificadas no arquivo requirements.txt. Esta abordagem garante que o AIAPad opere independentemente de outras aplicações Python instaladas no sistema, evitando conflitos de versão.

O frontend React é compilado durante a instalação, gerando arquivos estáticos otimizados que são servidos diretamente pelo Nginx. Esta abordagem melhora significativamente a performance de carregamento e reduz a carga no servidor de aplicação.

A configuração do banco de dados inclui a criação automática de tabelas e índices necessários, além da inserção de dados iniciais incluindo o usuário administrador padrão. O sistema gera automaticamente senhas seguras e chaves de criptografia, garantindo segurança adequada desde a primeira inicialização.

### Configuração de Segurança

A configuração de segurança do AIAPad implementa múltiplas camadas de proteção seguindo as melhores práticas para sistemas médicos. O firewall UFW é configurado automaticamente para permitir apenas tráfego necessário, bloqueando todas as outras conexões por padrão.

O sistema Fail2Ban é configurado para detectar e bloquear automaticamente tentativas de acesso malicioso, incluindo ataques de força bruta contra interfaces de login e tentativas de exploração de vulnerabilidades web. As regras são ajustadas especificamente para padrões de uso típicos de sistemas médicos.

Os certificados SSL são obtidos automaticamente através do Let's Encrypt e configurados para renovação automática, garantindo que a comunicação permaneça segura sem intervenção manual. O sistema implementa configurações SSL modernas incluindo Perfect Forward Secrecy e proteção contra ataques de downgrade.

As chaves de criptografia utilizadas para tokens JWT e outras operações criptográficas são geradas automaticamente durante a instalação utilizando geradores de números aleatórios criptograficamente seguros. Estas chaves são armazenadas com permissões restritivas e rotacionadas periodicamente.

### Configuração de Performance

O sistema de cache Redis é configurado para otimizar a performance através do armazenamento temporário de dados frequentemente acessados. A configuração inclui políticas de expiração inteligentes que balanceiam utilização de memória com performance de acesso.

O servidor web Nginx é configurado com otimizações específicas para servir conteúdo médico, incluindo compressão gzip para reduzir largura de banda, cache de arquivos estáticos para melhorar tempos de resposta, e configurações de timeout ajustadas para uploads de arquivos grandes.

O Gunicorn é configurado com múltiplos workers para aproveitar processadores multi-core, com o número de workers ajustado automaticamente baseado na capacidade do hardware. As configurações incluem timeouts estendidos para operações de processamento de lâminas e limites de memória para prevenir vazamentos.

O sistema de monitoramento coleta métricas de performance em tempo real, incluindo utilização de CPU, memória e disco, tempos de resposta de API e estatísticas de cache. Estas informações são utilizadas para otimização contínua e detecção precoce de problemas de performance.


## Documentação da API

### Visão Geral da API

A API RESTful do AIAPad oferece acesso programático a todas as funcionalidades do sistema através de endpoints bem definidos que seguem convenções REST padrão. A API utiliza JSON para troca de dados e implementa autenticação baseada em tokens JWT para garantir segurança adequada.

Todos os endpoints da API retornam códigos de status HTTP apropriados e mensagens de erro estruturadas que facilitam o desenvolvimento de aplicações cliente e a resolução de problemas. A documentação inclui exemplos de requisições e respostas para cada endpoint, facilitando a integração com sistemas externos.

A API implementa versionamento através de prefixos de URL, garantindo compatibilidade com versões futuras e permitindo evolução gradual sem quebrar integrações existentes. A versão atual utiliza o prefixo `/api/v1/` para todos os endpoints.

### Endpoints de Autenticação

#### POST /api/auth/login

Realiza autenticação de usuário e retorna tokens de acesso e refresh para sessões subsequentes.

**Parâmetros de Entrada:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Resposta de Sucesso (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@aiapad.com",
    "user_type": "admin",
    "first_name": "Administrador",
    "last_name": "Sistema"
  }
}
```

**Resposta de Erro (401):**
```json
{
  "error": "Invalid credentials",
  "message": "Username or password is incorrect"
}
```

#### POST /api/auth/refresh

Renova token de acesso utilizando token de refresh válido.

**Headers Necessários:**
```
Authorization: Bearer <refresh_token>
```

**Resposta de Sucesso (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### POST /api/auth/logout

Invalida tokens de acesso e refresh, encerrando a sessão do usuário.

**Headers Necessários:**
```
Authorization: Bearer <access_token>
```

**Resposta de Sucesso (200):**
```json
{
  "message": "Successfully logged out"
}
```

### Endpoints de Gerenciamento de Lâminas

#### GET /api/slides

Retorna lista paginada de lâminas acessíveis ao usuário autenticado.

**Parâmetros de Query:**
- `page`: Número da página (padrão: 1)
- `per_page`: Itens por página (padrão: 20, máximo: 100)
- `search`: Termo de busca para filtrar por nome ou descrição
- `stain_type`: Filtrar por tipo de coloração
- `uploaded_by`: Filtrar por usuário que fez upload (apenas admins)

**Headers Necessários:**
```
Authorization: Bearer <access_token>
```

**Resposta de Sucesso (200):**
```json
{
  "slides": [
    {
      "id": 1,
      "filename": "sample_slide.svs",
      "original_filename": "H&E_liver_biopsy.svs",
      "upload_date": "2025-07-15T10:30:00Z",
      "file_size": 2147483648,
      "width": 46000,
      "height": 32914,
      "levels": 4,
      "mpp_x": 0.2520,
      "mpp_y": 0.2520,
      "scanner_type": "Aperio AT2",
      "stain_type": "H&E",
      "status": "ready",
      "uploaded_by": {
        "id": 1,
        "username": "admin",
        "first_name": "Administrador",
        "last_name": "Sistema"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 1,
    "pages": 1
  }
}
```

#### GET /api/slides/{slide_id}

Retorna detalhes completos de uma lâmina específica.

**Headers Necessários:**
```
Authorization: Bearer <access_token>
```

**Resposta de Sucesso (200):**
```json
{
  "id": 1,
  "filename": "sample_slide.svs",
  "original_filename": "H&E_liver_biopsy.svs",
  "upload_date": "2025-07-15T10:30:00Z",
  "file_size": 2147483648,
  "width": 46000,
  "height": 32914,
  "levels": 4,
  "mpp_x": 0.2520,
  "mpp_y": 0.2520,
  "scanner_type": "Aperio AT2",
  "stain_type": "H&E",
  "status": "ready",
  "metadata": {
    "objective_power": 20,
    "scan_date": "2025-07-14T15:20:00Z",
    "compression": "JPEG",
    "bit_depth": 8
  },
  "annotations": [
    {
      "id": 1,
      "type": "rectangle",
      "x": 1000,
      "y": 1500,
      "width": 500,
      "height": 300,
      "label": "Área de interesse",
      "created_by": "admin",
      "created_at": "2025-07-15T11:00:00Z"
    }
  ]
}
```

#### GET /api/slides/{slide_id}/tile/{level}/{x}/{y}

Retorna tile específico de uma lâmina para visualização.

**Parâmetros de Path:**
- `slide_id`: ID da lâmina
- `level`: Nível de zoom (0 = máxima resolução)
- `x`: Coordenada X do tile
- `y`: Coordenada Y do tile

**Parâmetros de Query:**
- `width`: Largura do tile (padrão: 256)
- `height`: Altura do tile (padrão: 256)
- `format`: Formato da imagem (jpeg, png)

**Headers Necessários:**
```
Authorization: Bearer <access_token>
```

**Resposta de Sucesso (200):**
Retorna imagem binária no formato especificado.

#### GET /api/slides/{slide_id}/thumbnail

Retorna thumbnail da lâmina para visualização rápida.

**Parâmetros de Query:**
- `width`: Largura máxima (padrão: 200)
- `height`: Altura máxima (padrão: 200)

**Headers Necessários:**
```
Authorization: Bearer <access_token>
```

**Resposta de Sucesso (200):**
Retorna imagem JPEG do thumbnail.

### Endpoints de Upload

#### POST /api/upload/init

Inicializa processo de upload chunked para arquivo grande.

**Headers Necessários:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Parâmetros de Entrada:**
```json
{
  "filename": "large_slide.svs",
  "file_size": 5368709120,
  "file_hash": "d41d8cd98f00b204e9800998ecf8427e"
}
```

**Resposta de Sucesso (201):**
```json
{
  "upload_id": "550e8400-e29b-41d4-a716-446655440000",
  "chunk_size": 1048576,
  "total_chunks": 5120,
  "status": "initialized"
}
```

#### POST /api/upload/{upload_id}/chunk/{chunk_index}

Envia chunk específico do arquivo sendo uploadado.

**Headers Necessários:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Parâmetros de Form:**
- `chunk`: Arquivo binário do chunk

**Resposta de Sucesso (200):**
```json
{
  "chunk_index": 0,
  "status": "received",
  "checksum": "5d41402abc4b2a76b9719d911017c592"
}
```

#### POST /api/upload/{upload_id}/complete

Finaliza upload e inicia processamento da lâmina.

**Headers Necessários:**
```
Authorization: Bearer <access_token>
```

**Resposta de Sucesso (201):**
```json
{
  "message": "Upload completed successfully",
  "slide": {
    "id": 2,
    "filename": "processed_slide.svs",
    "status": "processing"
  },
  "upload_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### GET /api/upload/{upload_id}/status

Retorna status atual do upload em progresso.

**Headers Necessários:**
```
Authorization: Bearer <access_token>
```

**Resposta de Sucesso (200):**
```json
{
  "upload_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "uploading",
  "chunks_received": 1024,
  "total_chunks": 5120,
  "progress_percent": 20.0,
  "real_time_progress": 20.5,
  "upload_speed": "2.5 MB/s",
  "eta": "00:15:30",
  "elapsed_time": "00:05:12"
}
```

### Endpoints de Análise de IA

#### POST /api/slides/{slide_id}/analyze

Inicia análise de IA para detecção de doenças em lâmina específica.

**Headers Necessários:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Parâmetros de Entrada:**
```json
{
  "analysis_type": "disease_detection",
  "roi": {
    "x": 1000,
    "y": 1500,
    "width": 2000,
    "height": 1500
  },
  "parameters": {
    "sensitivity": 0.8,
    "model_version": "v2.1"
  }
}
```

**Resposta de Sucesso (202):**
```json
{
  "analysis_id": "analysis_123456",
  "status": "queued",
  "estimated_time": "00:02:30"
}
```

#### GET /api/slides/{slide_id}/analysis/{analysis_id}

Retorna resultados de análise de IA.

**Headers Necessários:**
```
Authorization: Bearer <access_token>
```

**Resposta de Sucesso (200):**
```json
{
  "analysis_id": "analysis_123456",
  "status": "completed",
  "analysis_type": "disease_detection",
  "results": {
    "confidence": 0.92,
    "detected_conditions": [
      {
        "condition": "Adenocarcinoma",
        "confidence": 0.89,
        "location": {
          "x": 1200,
          "y": 1800,
          "width": 400,
          "height": 300
        }
      }
    ],
    "summary": "Análise detectou possível adenocarcinoma com alta confiança"
  },
  "completed_at": "2025-07-15T12:15:00Z"
}
```

### Endpoints de Monitoramento

#### GET /api/health

Endpoint público para verificação de saúde do sistema.

**Resposta de Sucesso (200):**
```json
{
  "status": "healthy",
  "checks": {
    "cpu": {"status": "healthy", "value": 15.2},
    "memory": {"status": "healthy", "value": 45.8},
    "disk": {"status": "healthy", "value": 23.1},
    "database": {"status": "healthy"},
    "uploads": {"status": "healthy"}
  },
  "timestamp": "2025-07-15T13:30:00Z"
}
```

#### GET /api/health/detailed

Endpoint autenticado para verificação detalhada de saúde.

**Headers Necessários:**
```
Authorization: Bearer <access_token>
```

**Resposta de Sucesso (200):**
```json
{
  "health": {
    "status": "healthy",
    "checks": {
      "cpu": {"status": "healthy", "value": 15.2},
      "memory": {"status": "healthy", "value": 45.8},
      "disk": {"status": "healthy", "value": 23.1},
      "database": {"status": "healthy"},
      "uploads": {"status": "healthy"}
    }
  },
  "system": {
    "cpu": {"percent": 15.2, "count": 4},
    "memory": {
      "percent": 45.8,
      "total": 8589934592,
      "available": 4647108608,
      "used": 3942825984
    },
    "disk": {
      "percent": 23.1,
      "total": 107374182400,
      "free": 82589934592,
      "used": 24784247808
    },
    "uptime": 86400
  },
  "application": {
    "users": {"total": 5},
    "slides": {"total": 12},
    "storage": {
      "uploads_size": 25769803776,
      "database_size": 104857600
    }
  }
}
```

#### GET /api/metrics

Endpoint para métricas no formato Prometheus.

**Headers Necessários:**
```
Authorization: Bearer <access_token>
```

**Resposta de Sucesso (200):**
```
# HELP aiapad_cpu_percent CPU usage percentage
# TYPE aiapad_cpu_percent gauge
aiapad_cpu_percent 15.2

# HELP aiapad_memory_percent Memory usage percentage
# TYPE aiapad_memory_percent gauge
aiapad_memory_percent 45.8

# HELP aiapad_users_total Total number of users
# TYPE aiapad_users_total counter
aiapad_users_total 5

# HELP aiapad_slides_total Total number of slides
# TYPE aiapad_slides_total counter
aiapad_slides_total 12
```

### Códigos de Erro e Tratamento

A API utiliza códigos de status HTTP padrão para indicar sucesso ou falha de requisições. Todos os erros retornam um objeto JSON estruturado com informações detalhadas sobre o problema encontrado.

**Códigos de Status Comuns:**
- `200 OK`: Requisição processada com sucesso
- `201 Created`: Recurso criado com sucesso
- `400 Bad Request`: Parâmetros inválidos ou malformados
- `401 Unauthorized`: Token de autenticação inválido ou ausente
- `403 Forbidden`: Usuário não possui permissão para a operação
- `404 Not Found`: Recurso solicitado não encontrado
- `429 Too Many Requests`: Rate limit excedido
- `500 Internal Server Error`: Erro interno do servidor

**Formato de Resposta de Erro:**
```json
{
  "error": "validation_error",
  "message": "Invalid file format",
  "details": {
    "field": "file",
    "code": "INVALID_FORMAT",
    "supported_formats": ["SVS", "TIFF", "NDPI"]
  },
  "timestamp": "2025-07-15T13:30:00Z"
}
```

### Rate Limiting

A API implementa rate limiting para proteger contra abuso e garantir qualidade de serviço para todos os usuários. Os limites são aplicados por usuário e variam conforme o tipo de operação.

**Limites Padrão:**
- Autenticação: 5 tentativas por minuto
- Upload de lâminas: 10 uploads por hora
- Análise de IA: 5 análises por minuto
- Consultas gerais: 100 requisições por minuto

Os headers de resposta incluem informações sobre limites atuais:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642694400
```

Quando o limite é excedido, a API retorna status 429 com informações sobre quando tentar novamente:
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please try again later.",
  "retry_after": 60
}
```


## Guia de Troubleshooting

### Problemas Comuns de Instalação

#### Erro de Permissões Durante Instalação

**Sintoma:** Script de instalação falha com mensagens de "Permission denied"

**Causa:** Script não executado com privilégios administrativos adequados

**Solução:**
```bash
sudo ./install.sh
```

Certifique-se de que o usuário possui privilégios sudo e que o script tem permissões de execução:
```bash
chmod +x install.sh
```

#### Falha na Instalação de Dependências

**Sintoma:** Erro durante instalação de pacotes Python ou Node.js

**Causa:** Repositórios desatualizados ou dependências conflitantes

**Solução:**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt autoremove -y
sudo ./install.sh
```

Para problemas específicos com Python:
```bash
sudo apt install python3.11-dev python3.11-venv
```

#### Erro de Certificado SSL

**Sintoma:** Falha na obtenção de certificados Let's Encrypt

**Causa:** DNS não configurado corretamente ou firewall bloqueando porta 80

**Solução:**
1. Verificar configuração DNS:
```bash
nslookup lip.fm.usp.br
```

2. Verificar firewall:
```bash
sudo ufw status
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

3. Tentar obter certificado manualmente:
```bash
sudo certbot certonly --standalone -d lip.fm.usp.br
```

### Problemas de Performance

#### Alto Uso de CPU

**Sintoma:** Sistema lento, CPU constantemente acima de 80%

**Diagnóstico:**
```bash
htop
sudo iotop
```

**Soluções:**
1. Verificar processos Gunicorn:
```bash
sudo supervisorctl status
```

2. Ajustar número de workers:
```bash
sudo nano /opt/aiapad/backend/gunicorn.conf.py
# Reduzir workers para: workers = multiprocessing.cpu_count()
sudo supervisorctl restart aiapad-backend
```

3. Verificar análises de IA em execução:
```bash
curl -H "Authorization: Bearer <token>" http://localhost:5000/api/health/detailed
```

#### Alto Uso de Memória

**Sintoma:** Sistema com pouca memória disponível, possível swap excessivo

**Diagnóstico:**
```bash
free -h
sudo swapon --show
```

**Soluções:**
1. Limpar cache do Redis:
```bash
redis-cli FLUSHALL
```

2. Reiniciar aplicação:
```bash
sudo supervisorctl restart aiapad-backend
```

3. Configurar limite de memória para workers:
```bash
# Adicionar ao gunicorn.conf.py
max_requests = 500  # Reduzir de 1000
```

#### Lentidão no Upload de Arquivos

**Sintoma:** Uploads demoram muito tempo ou falham

**Diagnóstico:**
1. Verificar espaço em disco:
```bash
df -h /opt/aiapad
```

2. Verificar logs de upload:
```bash
tail -f /opt/aiapad/logs/aiapad.log | grep upload
```

**Soluções:**
1. Limpar uploads incompletos:
```bash
curl -X POST -H "Authorization: Bearer <admin_token>" http://localhost:5000/api/upload/cleanup
```

2. Verificar configuração Nginx:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### Problemas de Conectividade

#### Erro 502 Bad Gateway

**Sintoma:** Página não carrega, mostra erro 502

**Causa:** Backend não está respondendo

**Diagnóstico:**
```bash
sudo supervisorctl status aiapad-backend
curl http://localhost:5000/api/status
```

**Soluções:**
1. Reiniciar backend:
```bash
sudo supervisorctl restart aiapad-backend
```

2. Verificar logs:
```bash
tail -f /opt/aiapad/logs/aiapad.log
tail -f /opt/aiapad/logs/gunicorn_error.log
```

3. Verificar configuração:
```bash
cd /opt/aiapad/backend
source venv/bin/activate
python -c "from src.main import app; print('OK')"
```

#### Erro 504 Gateway Timeout

**Sintoma:** Requisições demoram muito e retornam timeout

**Causa:** Operações demoradas ou configuração inadequada de timeout

**Soluções:**
1. Ajustar timeouts no Nginx:
```bash
sudo nano /etc/nginx/sites-available/aiapad
# Adicionar na seção location /api/:
proxy_read_timeout 600s;
proxy_connect_timeout 600s;
sudo systemctl reload nginx
```

2. Ajustar timeouts no Gunicorn:
```bash
sudo nano /opt/aiapad/backend/gunicorn.conf.py
# Alterar: timeout = 600
sudo supervisorctl restart aiapad-backend
```

### Problemas de Banco de Dados

#### Erro de Conexão com Banco

**Sintoma:** Aplicação não consegue acessar banco de dados

**Diagnóstico:**
```bash
ls -la /opt/aiapad/backend/database/
sqlite3 /opt/aiapad/backend/database/production.db ".tables"
```

**Soluções:**
1. Verificar permissões:
```bash
sudo chown -R aiapad:aiapad /opt/aiapad/backend/database/
sudo chmod 664 /opt/aiapad/backend/database/production.db
```

2. Recriar banco se necessário:
```bash
cd /opt/aiapad/backend
source venv/bin/activate
python -c "from src.main import app, db; app.app_context().push(); db.create_all()"
```

#### Banco de Dados Corrompido

**Sintoma:** Erros de integridade ou dados inconsistentes

**Diagnóstico:**
```bash
sqlite3 /opt/aiapad/backend/database/production.db "PRAGMA integrity_check;"
```

**Soluções:**
1. Restaurar backup:
```bash
sudo /opt/aiapad/restore_backup.sh /opt/aiapad/backups/aiapad_backup_YYYYMMDD_HHMMSS.tar.gz
```

2. Reparar banco (último recurso):
```bash
sqlite3 /opt/aiapad/backend/database/production.db "REINDEX;"
sqlite3 /opt/aiapad/backend/database/production.db "VACUUM;"
```

### Problemas de Autenticação

#### Usuários Não Conseguem Fazer Login

**Sintoma:** Credenciais corretas rejeitadas

**Diagnóstico:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  http://localhost:5000/api/auth/login
```

**Soluções:**
1. Verificar usuário no banco:
```bash
sqlite3 /opt/aiapad/backend/database/production.db "SELECT * FROM user WHERE username='admin';"
```

2. Resetar senha do admin:
```bash
cd /opt/aiapad/backend
source venv/bin/activate
python -c "
from src.main import app, db
from src.models.user import User
with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    admin.set_password('admin123')
    db.session.commit()
    print('Senha resetada')
"
```

#### Tokens JWT Inválidos

**Sintoma:** Erro 401 em requisições autenticadas

**Causa:** Chave JWT alterada ou tokens expirados

**Soluções:**
1. Verificar configuração JWT:
```bash
grep JWT_SECRET_KEY /opt/aiapad/backend/config.py
```

2. Limpar tokens em cache:
```bash
redis-cli FLUSHALL
```

### Monitoramento e Logs

#### Verificar Status Geral do Sistema

```bash
# Status dos serviços
sudo systemctl status nginx
sudo systemctl status supervisor
sudo supervisorctl status

# Uso de recursos
htop
df -h
free -h

# Logs principais
tail -f /opt/aiapad/logs/aiapad.log
tail -f /var/log/nginx/error.log
tail -f /opt/aiapad/logs/gunicorn_error.log
```

#### Monitoramento de Performance

```bash
# Métricas da aplicação
curl -H "Authorization: Bearer <token>" http://localhost:5000/api/metrics

# Status detalhado
curl -H "Authorization: Bearer <token>" http://localhost:5000/api/health/detailed

# Estatísticas de upload
curl -H "Authorization: Bearer <admin_token>" http://localhost:5000/api/upload/stats
```

#### Análise de Logs

```bash
# Erros recentes
grep ERROR /opt/aiapad/logs/aiapad.log | tail -20

# Uploads com problema
grep "upload.*error" /opt/aiapad/logs/aiapad.log

# Tentativas de login falhadas
grep "login.*failed" /opt/aiapad/logs/aiapad.log

# Performance de análises de IA
grep "analysis.*completed" /opt/aiapad/logs/aiapad.log | tail -10
```

### Procedimentos de Emergência

#### Restauração Completa do Sistema

Em caso de falha crítica, siga estes passos para restauração completa:

1. **Parar todos os serviços:**
```bash
sudo supervisorctl stop all
sudo systemctl stop nginx
```

2. **Restaurar backup mais recente:**
```bash
cd /opt/aiapad/backups
ls -la aiapad_backup_*.tar.gz | tail -1
sudo tar -xzf aiapad_backup_YYYYMMDD_HHMMSS.tar.gz -C /
```

3. **Verificar permissões:**
```bash
sudo chown -R aiapad:aiapad /opt/aiapad
sudo chmod +x /opt/aiapad/backup.sh
```

4. **Reiniciar serviços:**
```bash
sudo systemctl start nginx
sudo supervisorctl start all
```

5. **Verificar funcionamento:**
```bash
curl http://localhost:5000/api/status
```

#### Migração para Novo Servidor

Para migrar o AIAPad para um novo servidor:

1. **No servidor antigo, criar backup completo:**
```bash
sudo /opt/aiapad/backup.sh
scp /opt/aiapad/backups/aiapad_backup_*.tar.gz user@new-server:/tmp/
```

2. **No servidor novo, instalar AIAPad:**
```bash
sudo ./install.sh
```

3. **Parar serviços e restaurar dados:**
```bash
sudo supervisorctl stop all
sudo tar -xzf /tmp/aiapad_backup_*.tar.gz -C /
sudo chown -R aiapad:aiapad /opt/aiapad
```

4. **Atualizar configurações específicas:**
```bash
sudo nano /etc/nginx/sites-available/aiapad
# Atualizar server_name se necessário
sudo systemctl reload nginx
```

5. **Reiniciar e verificar:**
```bash
sudo supervisorctl start all
curl https://new-domain.com/api/status
```

## Manutenção e Atualizações

### Rotinas de Manutenção

#### Manutenção Diária Automatizada

O sistema executa automaticamente as seguintes tarefas diárias:

1. **Backup incremental** às 02:00
2. **Limpeza de logs antigos** às 03:00
3. **Otimização do banco de dados** às 04:00
4. **Verificação de integridade** às 05:00

Para verificar o status das tarefas automáticas:
```bash
sudo crontab -u aiapad -l
sudo journalctl -u cron | grep aiapad
```

#### Manutenção Semanal

Execute semanalmente:

1. **Atualização do sistema operacional:**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt autoremove -y
```

2. **Verificação de espaço em disco:**
```bash
df -h /opt/aiapad
du -sh /opt/aiapad/uploads/*
```

3. **Análise de logs de erro:**
```bash
grep ERROR /opt/aiapad/logs/aiapad.log | tail -50
```

4. **Verificação de certificados SSL:**
```bash
sudo certbot certificates
```

#### Manutenção Mensal

Execute mensalmente:

1. **Backup completo para armazenamento externo:**
```bash
sudo /opt/aiapad/backup.sh
# Copiar backup para local seguro
```

2. **Otimização completa do banco:**
```bash
sqlite3 /opt/aiapad/backend/database/production.db "VACUUM; REINDEX;"
```

3. **Limpeza de cache:**
```bash
redis-cli FLUSHALL
sudo supervisorctl restart aiapad-backend
```

4. **Auditoria de segurança:**
```bash
sudo fail2ban-client status
sudo ufw status verbose
```

### Processo de Atualização

#### Atualização Automática

O sistema inclui script de atualização que pode ser executado com segurança:

```bash
sudo ./update.sh
```

O script executa automaticamente:
1. Backup pré-atualização
2. Download da nova versão
3. Atualização do backend
4. Atualização do frontend
5. Migração do banco de dados
6. Reinicialização dos serviços
7. Verificação de funcionamento

#### Atualização Manual

Para atualizações manuais ou customizadas:

1. **Criar backup:**
```bash
sudo /opt/aiapad/backup.sh
```

2. **Parar serviços:**
```bash
sudo supervisorctl stop aiapad-backend
```

3. **Atualizar código:**
```bash
cd /opt/aiapad/backend
sudo -u aiapad git pull origin main
sudo -u aiapad bash -c "source venv/bin/activate && pip install -r requirements.txt"
```

4. **Atualizar frontend:**
```bash
cd /opt/aiapad/frontend
sudo -u aiapad pnpm install
sudo -u aiapad pnpm run build
```

5. **Migrar banco de dados:**
```bash
cd /opt/aiapad/backend
sudo -u aiapad bash -c "source venv/bin/activate && python migrate.py"
```

6. **Reiniciar serviços:**
```bash
sudo supervisorctl start aiapad-backend
```

#### Rollback em Caso de Problemas

Se a atualização causar problemas:

```bash
sudo ./update.sh --rollback
```

Ou manualmente:
```bash
sudo supervisorctl stop aiapad-backend
sudo tar -xzf /opt/aiapad/backups/aiapad_pre_update_*.tar.gz -C /
sudo supervisorctl start aiapad-backend
```

## Considerações de Segurança

### Configurações de Segurança Implementadas

O AIAPad implementa múltiplas camadas de segurança seguindo as melhores práticas para sistemas médicos:

1. **Criptografia em trânsito:** Todas as comunicações utilizam HTTPS com certificados TLS 1.3
2. **Criptografia em repouso:** Dados sensíveis são criptografados no banco de dados
3. **Autenticação forte:** Tokens JWT com expiração configurável
4. **Autorização granular:** Controle de acesso baseado em roles
5. **Rate limiting:** Proteção contra ataques de força bruta
6. **Firewall:** UFW configurado para permitir apenas tráfego necessário
7. **Fail2Ban:** Detecção e bloqueio automático de IPs maliciosos
8. **Logs de auditoria:** Registro completo de atividades do sistema

### Compliance e Regulamentações

O sistema foi desenvolvido considerando requisitos de compliance médico:

- **LGPD:** Controles de privacidade e proteção de dados pessoais
- **CFM:** Diretrizes do Conselho Federal de Medicina para telemedicina
- **ANVISA:** Regulamentações para software médico
- **ISO 27001:** Controles de segurança da informação

### Recomendações de Segurança

#### Para Administradores

1. **Alterar senhas padrão imediatamente após instalação**
2. **Implementar política de senhas fortes**
3. **Configurar backup automático em local seguro**
4. **Monitorar logs de segurança regularmente**
5. **Manter sistema sempre atualizado**
6. **Restringir acesso SSH apenas para IPs autorizados**
7. **Implementar autenticação de dois fatores quando possível**

#### Para Usuários

1. **Utilizar senhas únicas e complexas**
2. **Fazer logout ao terminar sessão**
3. **Não compartilhar credenciais**
4. **Reportar atividades suspeitas**
5. **Manter navegador atualizado**

## Conclusão

O AIAPad representa uma solução abrangente e inovadora para análise de lâminas anatomopatológicas, combinando tecnologias modernas de inteligência artificial com uma interface intuitiva e funcionalidades robustas de gerenciamento. O sistema foi desenvolvido com foco na facilidade de uso, escalabilidade e segurança, atendendo às necessidades específicas de laboratórios de patologia, instituições de ensino e centros de pesquisa.

A arquitetura modular e bem documentada facilita a manutenção e permite extensões futuras, enquanto o processo de instalação automatizada reduz significativamente as barreiras técnicas para adoção. O suporte a múltiplos formatos de lâminas e scanners garante compatibilidade ampla com equipamentos existentes, maximizando o retorno sobre investimentos já realizados.

As funcionalidades de inteligência artificial oferecem suporte diagnóstico valioso, complementando a expertise de profissionais médicos sem substituir o julgamento clínico. O sistema de anotações colaborativas facilita o ensino e a pesquisa, criando um ambiente propício para o desenvolvimento contínuo do conhecimento em patologia.

A implementação de medidas de segurança robustas e compliance com regulamentações médicas garante que o sistema pode ser utilizado com confiança em ambientes clínicos reais. O monitoramento integrado e as ferramentas de troubleshooting facilitam a operação e manutenção do sistema.

O AIAPad está posicionado para contribuir significativamente para o avanço da patologia digital, oferecendo uma plataforma sólida para diagnóstico assistido por computador, ensino médico e pesquisa científica. A combinação de tecnologia avançada com facilidade de uso torna esta solução acessível para instituições de diferentes portes, democratizando o acesso a ferramentas de ponta em patologia digital.

---

**Suporte Técnico:**  
Email: admin@aiapad.com  
Documentação: https://docs.aiapad.com  
Issues: https://github.com/aiapad/issues  

**Desenvolvido por:** Manus AI  
**Versão da Documentação:** 1.0.0  
**Última Atualização:** 15 de Julho de 2025


# Analisador de Finanças Pessoais

CONFIGURAÇÃO:
1. Adicione seus extratos em `data/00_raw`
2. Execute os notebooks de 1 a 3
3. Veja as análises no notebook 10.

Workflow:
A cada mês, você deverá solicitar o extrato da conta do banco. Coloque-o em `data/00_raw`.
Em seguida, você realizará a limpeza automática, categorização semi-automática e reconciliação.
Quando seus dados estiverem preparados, o notebook `10_analyzer.ipynb` criará os dashboards para você.

Detalhes:
**Categorizador**
No início você adicionará manualmente as descrições que se encaixam em cada categoria na sua `category_lookup.json`. O categorizador usa esse json para fazer a primeira categorização. Caso queria mudar algo, uma plataforma iterativa te permite mudanças manuais em `02_categorizer.ipynb`.
Não se preocupe, a quantidade de trabalho manual diminui com o tempo. À medida que você constrói seu banco de dados com transações categorizadas, o aprendizado de máquina começará a fazer isso por você.

**Reconciliação**
Você também pode verificar no seu banco qual é o saldo de cada mês. Isso garante que seus dados estejam corretos.

![dashboard](<screenshots/category-dashboard.png>)


![alt text](<screenshots/cash-flow-dashboard1.png>)
![alt text](<screenshots/cash-flow-dashboard2.png>)


**MAIS DASHBOARDS E RECURSOS DE ANÁLISE EM BREVE**

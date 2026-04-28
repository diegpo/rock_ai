import re
import os
from datetime import datetime
from tools.base_tool import BaseTool

TSS_BASE_URL = os.getenv("TSS_URL", "https://[CONFIGURE_NO_ENV]/tss")


class TSSExtractContextTool(BaseTool):
    """Extrai dados do chamado (cliente, ID, ticket, prefeitura)."""
    name = "tss_extract_context"

    def run(self, context=None) -> dict:
        return {
            "success": True,
            "data": (
                "📋 **Contexto identificado — Erro TSS/NFS-e**\n\n"
                "Identifiquei que se trata de um erro de transmissão de NFS-e via TSS.\n"
                "Vou guiar o atendimento passo a passo."
            )
        }


class TSSCheckUrlTool(BaseTool):
    """Orienta o analista a verificar se o TSS está online."""
    name = "tss_check_url"

    def run(self, context=None) -> dict:
        tss_url = os.getenv("TSS_URL", "")

        if tss_url:
            curl_cmd = f"curl -s -o /dev/null -w \"%{{http_code}}\" {tss_url}/api/health"
        else:
            curl_cmd = "curl -s -o /dev/null -w \"%{http_code}\" https://[URL_DO_TSS_NO_TCLOUD]/tss/api/health"

        return {
            "success": True,
            "data": (
                "**PASSO 1 — Verificar se o TSS está online**\n\n"
                f"Execute este curl para testar a URL do TSS do cliente:\n"
                f"```\n{curl_cmd}\n```\n\n"
                "Resultados esperados:\n"
                "- `200` → TSS online ✅ (problema pode ser versão ou configuração)\n"
                "- `503` ou `404` → TSS com problema ⚠️ (reiniciar o serviço no tcloud)\n"
                "- `000` → TSS offline ❌ (serviço parado, acionar suporte tcloud)\n\n"
                "Após testar, informe o retorno aqui."
            )
        }


class TSSRequestLogTool(BaseTool):
    """Solicita o log do TSS ao analista."""
    name = "tss_request_log"

    def run(self, context=None) -> dict:
        return {
            "success": True,
            "data": (
                "**PASSO 2 — Coletar o log do TSS**\n\n"
                "No tcloud, acesse:\n"
                "> Serviços → TSS → Guia **Logs** → arquivo **console_tss.log**\n\n"
                "Cole o conteúdo do log aqui no chat para eu analisar.\n\n"
                "💡 *Dica: Se o arquivo for muito grande, cole as últimas 100 linhas.*"
            )
        }


class TSSAnalyzeLogTool(BaseTool):
    """
    Analisa o log colado pelo analista.
    Procura por erros/fatais e retorna trechos com contexto (2 linhas antes e depois).
    """
    name = "tss_analyze_log"

    # Palavras-chave que indicam problema
    ERROR_PATTERNS = re.compile(
        r"(ERROR|Error|error|FATAL|Fatal|fatal|Exception|EXCEPTION|NullPointer|"
        r"Caused by|StackTrace|Traceback|Connection refused|timeout|Timeout|"
        r"NFS|prefeitura|transmiss)",
        re.IGNORECASE
    )

    def run(self, context=None) -> dict:
        log_text = (context or {}).get("log", "")

        if not log_text:
            return {
                "success": False,
                "data": "Nenhum log recebido para análise. Por favor cole o conteúdo do console_tss.log."
            }

        lines = log_text.splitlines()
        findings = []
        seen = set()

        for i, line in enumerate(lines):
            if self.ERROR_PATTERNS.search(line):
                # Pega 2 linhas antes e 2 depois
                start = max(0, i - 2)
                end   = min(len(lines), i + 3)

                # Evita duplicar trechos sobrepostos
                key = (start, end)
                if key in seen:
                    continue
                seen.add(key)

                snippet = []
                for j in range(start, end):
                    prefix = ">>> " if j == i else "    "
                    snippet.append(f"{prefix}{lines[j]}")

                findings.append("\n".join(snippet))

        if not findings:
            return {
                "success": True,
                "data": (
                    "✅ Nenhum erro crítico encontrado no log fornecido.\n\n"
                    "Possíveis causas para o erro de transmissão:\n"
                    "- Versão do TSS desatualizada (requerida: 12.1.2410_NW)\n"
                    "- Configuração de prefeitura incorreta\n"
                    "- Certificado digital vencido\n\n"
                    "Verifique a versão atual do TSS no tcloud e compare com a requerida."
                )
            }

        resultado = f"🔍 **Encontrei {len(findings)} ocorrência(s) relevante(s) no log:**\n\n"
        resultado += "\n\n---\n\n".join(
            f"**Ocorrência {i+1}:**\n```\n{f}\n```"
            for i, f in enumerate(findings[:10])  # máximo 10 ocorrências
        )

        resultado += (
            "\n\n---\n\n"
            "**Próximos passos:**\n"
            "1. Verifique se os erros acima são recentes (mesma data/hora do chamado)\n"
            "2. Confirme a versão do TSS — para Mauá-SP é necessário: `12.1.2410_NW`\n"
            "3. Se a versão estiver correta, verifique as configurações de prefeitura no TSS\n"
            "4. Se necessário, reinicie o serviço TSS no tcloud após corrigir"
        )

        return {"success": True, "data": resultado}
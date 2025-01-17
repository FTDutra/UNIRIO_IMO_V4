import logging
from elfs.builders import olx_bld
from elfs.builders import vivareal_bld
from elfs.builders import zapimoveis_bld

class Builders:
    def __init__(self):
        """
        Cria classe que chama os builders. Para entender as funções, olhar os arquivos da pasta builder.
        """

        self._configure_logger()

    def _configure_logger(self):
        """Configura o logger para registro das operações executadas."""
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def executar_builder(self,
                         builder,
                         action=3,
                         delete_after=True):
        """
        Executa o builder em questão.
        Depende dos seguintes parâmetros:
        :param builder: Pode ser 'zapimoveis', 'vivareal', 'olx'.
        :param action: Define a ação que será feita. Por padrão é [3]. Cria o csv temporario e cria o arquivo final na pasta 'csv'
        :param delete_after: Define se, após a execução, o arquivo temporário será deletado. Por padrão True.
        :return: True | False
        """

        try:
            if builder == "zapimoveis":
                zapimoveis_bld.ZapimoveisBuilder(action=action, delete_after=delete_after)
            elif builder == "vivareal":
                vivareal_bld.VivarealBuilder(action=action, delete_after=delete_after)
            elif builder == "olx":
                olx_bld.OlxBuilder(action=action, delete_after=delete_after)

            self.logger.info(f"Operação concluída com sucesso. O builder selecionado foi {builder}, com a ação {action}. Delete after: {delete_after}.")
            return True

        except Exception as e:
            self.logger.info("Falha ao concluir a operação.")
            return False
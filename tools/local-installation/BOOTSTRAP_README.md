# Arranque verificable desde Python limpio

Distribuir esta carpeta de herramientas por un canal de confianza independiente
del ZIP. El bootstrap, `local_installation.py`, el lock y los módulos de
`individual_cli.py` son parte de esa raíz de confianza. No extraerlos del ZIP
sin autenticar para ejecutarlos. Conservar y comparar el fingerprint del editor
por un canal independiente; nunca aceptarlo automáticamente desde el paquete.

```powershell
.\INSTALL_INDIVIDUAL.ps1 -Python 'C:\Python312\python.exe' -Archive 'C:\Entrega\individual.zip' -Signature 'C:\Entrega\individual.zip.sig.json' -InstallRoot "$env:LOCALAPPDATA\Emergency\Individual" -PublisherFile 'C:\Confianza\publisher.json' -ExpectedPublisherFingerprint 'FINGERPRINT_SHA256_CONFIABLE_DE_64_HEX_MINUSCULAS'
```

Requisito: Python 3.12 x64 Windows instalado. El bootstrap inicial importa solo
biblioteca estándar y `local_installation.py` estándar. Prevalida estructura y
límites ZIP sin ejecutar código del paquete. Extrae únicamente tres wheels cuyos
tamaños y hashes coincidan con el lock externo: cryptography 50.0.2, cffi 2.1.1 y
pycparser 3.12. El lock procede del cotejo realizado con hashes publicados de PyPI;
no se confía en un lock incluido en el ZIP para esta primera verificación.

Crea un venv persistente del verificador, sin cambios globales, en
`<InstallRoot>/bootstrap-verifiers/<hash-del-lock-externo>`, e instala esos wheels
con pip aislado, sin índice/red, solo binarios y hashes obligatorios. Invoca después
el CLI externo de confianza con el editor/fingerprint independientes. El CLI
verifica firma, instala la versión y prepara el runtime completo separado. No
activa automáticamente la versión ni autoriza uso clínico. El recibo local controla
el conjunto de archivos y cada hash antes de reutilizar el verificador. Se rechazan
archivos extra, enlaces y bytes alterados. Este recibo local no protege frente a
un proceso malicioso ejecutado por el mismo usuario. Los wheels de preparación
temporales son públicos y no contienen casos, claves privadas ni tokens.

La instalación imprime su versión real y los argumentos `next_activate` y
`next_serve`. Con el mismo Python 3.12 instalado, aunque no tenga cryptography:

```powershell
.\START_INDIVIDUAL.ps1 -Python 'C:\Python312\python.exe' -InstallRoot "$env:LOCALAPPDATA\Emergency\Individual" -Action activate -Version 'VERSION_EXACTA_DEVUELTA_POR_INSTALL'
.\START_INDIVIDUAL.ps1 -Python 'C:\Python312\python.exe' -InstallRoot "$env:LOCALAPPDATA\Emergency\Individual" -Action serve
```

Para rollback se usa `-Action rollback -Version 'VERSION_ANTERIOR_INSTALADA'`.
Estas acciones no requieren de nuevo el ZIP: verifican el verificador persistente
y ejecutan el CLI externo de confianza, que autentica íntegramente la versión.
En Windows el bootstrap mantiene un Job Object antes de enviar la compuerta
`START` al CLI; al terminar abruptamente se elimina también su árbol de procesos.
Una prueba real comprueba la muerte del hijo y nieto propios, y otra verifica que
fallar la asignación al Job no permite abrir la compuerta.
Actualizar implica ejecutar de nuevo `INSTALL_INDIVIDUAL.ps1` con el nuevo ZIP y
su firma, conservando el mismo editor/fingerprint de confianza, y activar su
versión explícitamente. No se presupone Python de otra aplicación propietaria.

Las pruebas sintéticas cubren extracción, manipulación, traversal, ausencia de
dependencias, rechazo sin fingerprint y contrato de invocación offline. El test
del contrato usa mocks de procesos y no se presenta como instalación física.
La recepción física del artefacto firmado debe probarse adicionalmente sobre su
SHA exacto.

`CLINICALLY_PENDING` · `NO_GO_CLINICAL_RELEASE`

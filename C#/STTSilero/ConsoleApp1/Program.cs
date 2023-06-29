using System.Diagnostics;
using System.Net;
using System.Text;


namespace STTSilero
{
    /// <summary>
    /// STT обработчик silero online
    /// </summary>
    public class STTSilero
    {
        bool canceledToken;
        /// <summary>
        /// идентификатор процесса
        /// </summary>
        string processId;

        //TODO перенести в настройки обработчика
        const string apiToken = "my_api_token";
        const string apiUrl = "https://api.silero.ai/transcribe";

        /// <summary>
        /// событие, возращающее результаты распознования речи
        /// </summary>
        /// <param name="processResult"></param>
        public event ISTTProcessor.ProcessCompleteEvent onProcessComplete;


        /// <summary>
        /// Запуск распознователя
        /// </summary>
        /// <param name="canceledToken">токен для отслеживания завершения задачи</param>
        /// <returns></returns>
        public bool Run(bool canceledToken, string processId)
        {

            this.processId = processId;
            this.canceledToken = canceledToken;
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);

            Task.Run(() => {
                while (!canceledToken)
                {

                    try
                    {

                        //поиск новых файлов для процессинга
                        var t = (new DirectoryInfo($"./{processId}/complete")).GetFiles("*.wav").MinBy(x => x.LastWriteTime);

                        if (t != null)
                        {


                            try
                            {
                                var bytes = File.ReadAllBytes(t.FullName);
                                var payload = Convert.ToBase64String(bytes);

                                var httpWebRequest = (HttpWebRequest)WebRequest.Create(apiUrl);
                                httpWebRequest.ContentType = "application/json";
                                httpWebRequest.Method = "POST";

                                using (var streamWriter = new StreamWriter(httpWebRequest.GetRequestStream()))
                                {

                                    //object json - //TODO уточнить формат посылки

                                    //streamWriter.Write(json);
                                }

                                var httpResponse = (HttpWebResponse)httpWebRequest.GetResponse();
                                var responseStream = httpResponse.GetResponseStream();

                                using (var streamReader = new StreamReader(responseStream))
                                {
                                    var result = streamReader.ReadToEnd();

                                    if (result.Trim().Length > 0)
                                        onProcessComplete(result);
                                }
                            }
                            catch { }

                            File.Delete(t.FullName);
                        }

                        Thread.Sleep(100);
                    }
                    catch (Exception err) { }
                }
            });

            return true;
        }

        /// <summary>
        /// остановка распознователя
        /// </summary>
        /// <returns></returns>
        public bool Stop()
        {
            canceledToken = true;
            return true;
        }

        void Dispose()
        {

            canceledToken = true;
            var deleted = true;

            while (deleted)
            {
                try
                {
                    Directory.Delete($"./{processId}/complete", true);
                }
                catch { }
            }


        }
    }

}

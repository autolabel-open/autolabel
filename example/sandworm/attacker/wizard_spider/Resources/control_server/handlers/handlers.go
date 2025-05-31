package handlers

import (
	"attackevals.mitre-engenuity.org/control_server/handlers/emotet"
	"attackevals.mitre-engenuity.org/control_server/handlers/exaramel"
	"attackevals.mitre-engenuity.org/control_server/handlers/https"
	"attackevals.mitre-engenuity.org/control_server/handlers/simplehttp"
	"attackevals.mitre-engenuity.org/control_server/handlers/trickbot"
	"attackevals.mitre-engenuity.org/control_server/logger"
)

// StartHandlers starts the C2 handlers
func StartHandlers() {
	restAPIAddr := "127.0.0.1:9999"

	// To Do - handlers should pull bind information from a configuration file
	simplehttp.StartHandler("0.0.0.0:8080", restAPIAddr)
	logger.Success("Started simpleHTTP handler on 0.0.0.0:8080")

	https.StartHandler("0.0.0.0:443", restAPIAddr, "", "")
	logger.Success("Started HTTPS handler on 0.0.0.0:443")

	trickbot.StartHandler("0.0.0.0:447", restAPIAddr)
	logger.Success("Started TrickBot handler on 0.0.0.0:447")

	emotet.StartHandler("0.0.0.0:80", "127.0.0.1:9999")
	logger.Success("Started Emotet handler on 0.0.0.0:80")

	exaramel.StartHandler("0.0.0.0:8443", "127.0.0.1:9999", "", "")
	logger.Success("Started Exaramel handler on 0.0.0.0:8443")
	// To do - each handler should send a signal to indicate it started successfully
}

// StopHandlers stops all C2 handlers
func StopHandlers() {
	simplehttp.StopHandler()
	logger.Success("Terminated simpleHTTP handler")
	//logger.Info("Stoping C2 handlers")
	trickbot.StopHandler()
	// To do - each handler should send a signal to indicate it stopped gracefully
}

// StopHandlerByName stops the C2 handler specified by handlerName
func StopHandlerByName(handlerName string) {
	logger.Info("Stopping handler: ", handlerName)
	// need to implement
}

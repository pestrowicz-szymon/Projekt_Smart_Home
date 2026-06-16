import pino from 'pino';

const isDev = process.env.NODE_ENV === 'development';

const transport = isDev
	? {
			target: 'pino-pretty',
			options: {
				colorize: true,
				translateTime: 'SYS:standard',
				ignore: 'pid,hostname',
				singleLine: false
			}
		}
	: undefined;

export const logger = pino(
	{
		level: process.env.LOG_LEVEL || (isDev ? 'debug' : 'info'),
		transport
	},
	pino.destination(1) // stdout
);

// Create child loggers for different modules
export const createLogger = (name: string) => logger.child({ module: name });

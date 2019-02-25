import { AzureFunction, Context } from "@azure/functions"
import { Namespace, SendableMessageInfo } from "@azure/service-bus"
import { dateTimeOffset } from "@azure/amqp-common/typings/lib/util/constants";

const RETRY_LIMIT = 5;
const RETRY_MULTIPLIER_SECONDS = 5;

const serviceBusClient = Namespace.createFromConnectionString(process.env['ServiceBusConnectionString']);
const queueClient = serviceBusClient.createQueueClient('queue');
const sender = queueClient.getSender();

const serviceBusQueueTrigger: AzureFunction = async function (context: Context, message: any): Promise<void> {
    try {
        context.log('ServiceBus queue trigger function processed message', message);
        throw new Error('Something went wrong');
    }
    catch (err) {
        let retry_property = context.bindingData['user_properties']['retry-count'];
        let retry_count =  retry_property != null ? retry_property : 0
        if(retry_count < RETRY_LIMIT) {
            retry_count++;
            let delay_seconds = retry_count * RETRY_MULTIPLIER_SECONDS;
            context.log(`Scheduling for retry #${retry_count} delayed for ${delay_seconds} seconds...`);
            let newMsg: SendableMessageInfo = {
                body: message,
                userProperties: {'retry-count': retry_count},
                messageId: context.bindingData['messageId']
            }
            await sender.scheduleMessage(new Date(), newMsg);
        }
        else {
            context.log.error('Exceeded retry limit')
            // You could publish to a poison queue to handle later
        }
    }

};

export default serviceBusQueueTrigger;
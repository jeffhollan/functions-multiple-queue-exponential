import { AzureFunction, Context, HttpRequest } from "@azure/functions"

const httpTrigger: AzureFunction = async function (context: Context, req: HttpRequest): Promise<void> {
    context.log('HTTP trigger function processed a request.');

    context.bindings['msg'] = 'JavaScript queue message'

    context.res = {
        status: 200
    }
};

export default httpTrigger;

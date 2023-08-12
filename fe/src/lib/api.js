const url = 'http://localhost:8000';

function CustomException(message, status) {
  const error = new Error(message);
  error.status = status;
  return error;
}

const queue = async (name, start) => {
  const response = await fetch(`${url}/ir/${name}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ start })
  });
	if (!response.ok) {
    const body = await response.json();
    console.error(`${response.status} ${body.detail}`);
		throw new CustomException(body.detail, response.status);
	}
  return response.json();
};

const get = async (name) => {
  const response = await fetch(`${url}/ir/${name}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  });
  return response.json();
};

const create = async (name, workflowId, active = true) => {
  const response = await fetch(`${url}/ir`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, wf_id: workflowId, active })
  });
  return response.json();
};

export const ingestion = { queue, get, create };

const update = async (locations, workflowId) => {
  const response = await fetch(`${url}/workflows/${workflowId}/locations`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(locations)
  });
  return response.json();
};

export const locations = { update };

const createInstance = async (workflowId) => {
  const response = await fetch(`${url}/workflows/create_instance?wf_id=${workflowId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
    // body: {}
  });
  return response.json();
};

const enqueue = async (workflowId) => {
  const response = await fetch(`${url}/workflows/${workflowId}/enqueue`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: {}
  });
  return response.json();
};

const create_and_enqueue = async (workflowId) => {
  const response = await createInstance(workflowId);
  await enqueue(response);
  return response;
};

export const workflows = { createInstance, enqueue, create_and_enqueue };

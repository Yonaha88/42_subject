/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   scheduler.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/06 12:22:46 by kyonaha           #+#    #+#             */
/*   Updated: 2026/10/06 12:22:47 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

static t_request	make_request(t_coder *c)
{
	t_request	req;

	req.coder_id = c->id;
	req.ticket = c->table->next_ticket;
	c->table->next_ticket++;
	req.key = req.ticket;
	if (c->table->args.scheduler == CODEX_EDF)
	{
		pthread_mutex_lock(&c->state_mutex);
		req.key = c->last_compile + c->table->args.time_to_burnout * 1000L;
		pthread_mutex_unlock(&c->state_mutex);
	}
	return (req);
}

void	request_dongles(t_coder *c)
{
	t_request	req;

	req = make_request(c);
	dongle_enqueue(c->first, req);
	dongle_enqueue(c->second, req);
}

int	try_take(t_coder *c)
{
	long	now;

	now = now_us();
	if (!dongle_is_first(c->first, c->id)
		|| !dongle_is_first(c->second, c->id)
		|| !dongle_usable(c->first, now)
		|| !dongle_usable(c->second, now))
		return (0);
	dongle_take(c->first, c->id);
	dongle_take(c->second, c->id);
	return (1);
}

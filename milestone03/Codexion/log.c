/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   log.c                                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/06 12:23:11 by kyonaha           #+#    #+#             */
/*   Updated: 2026/10/06 12:23:12 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

static int	put_nbr(char *buf, long n)
{
	char	digits[20];
	int		len;
	int		i;

	len = 0;
	if (n <= 0)
		digits[len++] = '0';
	while (n > 0)
	{
		digits[len] = '0' + n % 10;
		n /= 10;
		len++;
	}
	i = 0;
	while (i < len)
	{
		buf[i] = digits[len - 1 - i];
		i++;
	}
	return (len);
}

static void	write_line(t_table *t, long ts, int id, const char *msg)
{
	char	buf[96];
	int		len;
	int		i;

	len = put_nbr(buf, (ts - t->start) / 1000);
	buf[len++] = ' ';
	len += put_nbr(buf + len, id);
	buf[len++] = ' ';
	i = 0;
	while (msg[i])
		buf[len++] = msg[i++];
	buf[len++] = '\n';
	write(1, buf, len);
}

void	log_state(t_coder *c, const char *msg)
{
	pthread_mutex_lock(&c->table->log_mutex);
	if (!is_stopped(c->table))
		write_line(c->table, now_us(), c->id, msg);
	pthread_mutex_unlock(&c->table->log_mutex);
}

int	log_burnout(t_coder *c)
{
	long	now;
	int		burned;

	pthread_mutex_lock(&c->table->log_mutex);
	now = now_us();
	pthread_mutex_lock(&c->state_mutex);
	burned = (now - c->last_compile > c->table->args.time_to_burnout * 1000L);
	pthread_mutex_unlock(&c->state_mutex);
	if (burned && !is_stopped(c->table))
	{
		set_stop(c->table);
		write_line(c->table, now, c->id, "burned out");
	}
	pthread_mutex_unlock(&c->table->log_mutex);
	return (burned);
}

long	log_compile(t_coder *c)
{
	long	now;
	int		late;

	pthread_mutex_lock(&c->table->log_mutex);
	now = now_us();
	pthread_mutex_lock(&c->state_mutex);
	late = (now - c->last_compile > c->table->args.time_to_burnout * 1000L);
	if (!late)
		c->last_compile = now;
	pthread_mutex_unlock(&c->state_mutex);
	if (late && !is_stopped(c->table))
	{
		set_stop(c->table);
		write_line(c->table, now, c->id, "burned out");
	}
	else if (!is_stopped(c->table))
	{
		write_line(c->table, now, c->id, "has taken a dongle");
		write_line(c->table, now, c->id, "has taken a dongle");
		write_line(c->table, now, c->id, "is compiling");
	}
	pthread_mutex_unlock(&c->table->log_mutex);
	if (late)
		return (-1);
	return (now);
}

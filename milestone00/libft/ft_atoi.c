/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_atoi.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/04/25 16:45:56 by kyonaha           #+#    #+#             */
/*   Updated: 2026/05/01 15:19:06 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

int	ft_atoi(const char *numptr)
{
	long	num;
	int		sign;
	int		idx;

	num = 0;
	idx = 0;
	sign = 0;
	while (numptr[idx] == ' ' || (9 <= numptr[idx] && numptr[idx] <= 13))
		idx++;
	if (numptr[idx] == '-')
		sign = 1;
	if (numptr[idx] == '-' || numptr[idx] == '+')
		idx++;
	while ('0' <= numptr[idx] && numptr[idx] <= '9')
	{
		num *= 10;
		num += numptr[idx] - '0';
		idx++;
	}
	if (sign)
		num *= -1;
	return ((int)num);
}
